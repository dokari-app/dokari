import Foundation
import AVFoundation

/// What the coaching server answers (see server.py). Everything is optional-safe: an error answer has no attempts or cues.
struct CoachAnswer: Decodable {
    var seconds: Double?
    var attempts: [Attempt]
    var events: [Cue]
    var error: String?

    struct Attempt: Decodable, Identifiable {
        var attempt: Int
        var start: Double
        var end: Double
        var activity: String?
        var objectives: [String: Objective]?
        var id: Int { attempt }
        var missed: [String] {
            (objectives ?? [:]).filter { $0.value.status == "missed" }.map { $0.key.replacingOccurrences(of: "_", with: " ") }.sorted()
        }
    }
    struct Objective: Decodable { var status: String }
    struct Cue: Decodable, Identifiable {
        var t: Double
        var kind: String
        var text: String
        var activity: String?
        var id: String { "\(t)-\(text)" }
    }

    enum CodingKeys: String, CodingKey { case seconds, attempts, events, error }
    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        seconds = try c.decodeIfPresent(Double.self, forKey: .seconds)
        attempts = try c.decodeIfPresent([Attempt].self, forKey: .attempts) ?? []
        events = try c.decodeIfPresent([Cue].self, forKey: .events) ?? []
        error = try c.decodeIfPresent(String.self, forKey: .error)
    }
}

struct CoachError: LocalizedError {
    var message: String
    var errorDescription: String? { message }
}

/// Shrinks a large video (for example 4K, 800 MB) to 720p before it is sent. Frame rate is kept.
enum VideoShrinker {
    static func shrink(_ input: URL) async throws -> URL {
        let asset = AVURLAsset(url: input)
        guard let session = AVAssetExportSession(asset: asset, presetName: AVAssetExportPreset1280x720) else {
            throw CoachError(message: "This video can't be prepared for sending.")
        }
        let out = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString + ".mov")
        session.shouldOptimizeForNetworkUse = true
        if #available(iOS 18.0, *) {
            try await session.export(to: out, as: .mov)
        } else {
            session.outputURL = out
            session.outputFileType = .mov
            await session.export()
            if session.status != .completed {
                throw CoachError(message: "The video could not be prepared for sending (\(session.error?.localizedDescription ?? "unknown error")).")
            }
        }
        return out
    }
}

struct CoachClient {
    var address: String
    var token: String

    private func baseURL() throws -> URL {
        var base = address.trimmingCharacters(in: .whitespacesAndNewlines)
        while base.hasSuffix("/") { base.removeLast() }
        if !base.lowercased().hasPrefix("http") { base = "http://" + base }
        guard let url = URL(string: base) else {
            throw CoachError(message: "The server address doesn't look right.")
        }
        return url
    }

    /// Quick check that the Mac can be reached, so a problem shows up in seconds and not after a long wait.
    func check() async throws {
        let url = try baseURL().appendingPathComponent("health")
        var request = URLRequest(url: url)
        request.timeoutInterval = 8
        do {
            let (_, response) = try await URLSession.shared.data(for: request)
            guard (response as? HTTPURLResponse)?.statusCode == 200 else {
                throw CoachError(message: "The server answered, but not as the coach. Check the address.")
            }
        } catch let error as CoachError {
            throw error
        } catch {
            let code = (error as NSError).code
            throw CoachError(message: "Can't reach the coach at \(address) (error \(code)). Check that the server is running, that the phone and the Mac are on the same Wi-Fi, and that Local Network is switched on for Skill Sphere in the iPhone's Settings.")
        }
    }

    func analyse(video: URL) async throws -> CoachAnswer {
        guard let url = URL(string: try baseURL().absoluteString + "/coach?only=tennis") else {
            throw CoachError(message: "The server address doesn't look right.")
        }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.timeoutInterval = 900                       // reading a long video takes a while
        request.setValue(token.trimmingCharacters(in: .whitespacesAndNewlines), forHTTPHeaderField: "X-Token")
        request.setValue("video/quicktime", forHTTPHeaderField: "Content-Type")

        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 900
        config.timeoutIntervalForResource = 3600
        let session = URLSession(configuration: config)

        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await session.upload(for: request, fromFile: video)
        } catch {
            let code = (error as NSError).code
            throw CoachError(message: "Could not reach the coach (\(error.localizedDescription), error \(code)). Is the server running, and are the phone and the Mac on the same Wi-Fi?")
        }
        guard let answer = try? JSONDecoder().decode(CoachAnswer.self, from: data) else {
            throw CoachError(message: "The coach sent something unexpected.")
        }
        if let message = answer.error { throw CoachError(message: message) }
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw CoachError(message: "The coach answered with an error.")
        }
        return answer
    }
}
