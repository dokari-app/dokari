import AVKit
import PhotosUI
import SwiftUI

/// A video picked from the photo library, copied to a file we own.
struct PickedMovie: Transferable {
    let url: URL
    static var transferRepresentation: some TransferRepresentation {
        FileRepresentation(contentType: .movie) { movie in
            SentTransferredFile(movie.url)
        } importing: { received in
            let copy = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString + ".mov")
            try FileManager.default.copyItem(at: received.file, to: copy)
            return PickedMovie(url: copy)
        }
    }
}

struct ContentView: View {
    @AppStorage("address") private var address = ""
    @AppStorage("token") private var token = ""

    enum Phase {
        case idle
        case working(String)
        case failed(String)
        case result(Coaching, CoachAnswer)
    }

    @State private var phase: Phase = .idle
    @State private var showCamera = false
    @State private var showSettings = false
    @State private var picked: PhotosPickerItem?

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    switch phase {
                    case .idle: start
                    case .working(let text): working(text)
                    case .failed(let message): failed(message)
                    case .result(let coaching, let answer): ResultView(coaching: coaching, answer: answer) { phase = .idle }
                    }
                }
                .padding(16)
            }
            .navigationTitle("Skill Sphere")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button { showSettings = true } label: { Image(systemName: "gearshape") }
                }
            }
            .sheet(isPresented: $showSettings) { settings }
            .fullScreenCover(isPresented: $showCamera) {
                CameraRecorder { url in
                    showCamera = false
                    if let url { send(url) }
                }
                .ignoresSafeArea()
            }
            .onChange(of: picked) { _, item in
                guard let item else { return }
                picked = nil
                phase = .working("Opening the video…")
                Task {
                    do {
                        guard let movie = try await item.loadTransferable(type: PickedMovie.self) else {
                            phase = .failed("That video could not be opened.")
                            return
                        }
                        send(movie.url)
                    } catch {
                        phase = .failed("That video could not be opened (\(error.localizedDescription)).")
                    }
                }
            }
            .onAppear { if address.isEmpty { showSettings = true } }
        }
    }

    // MARK: screens

    private var start: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("Film a few swings. Your coach watches and says very little.")
                .foregroundStyle(.secondary)
            Button { showCamera = true } label: {
                Label("Record a video", systemImage: "video.fill").frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)
            PhotosPicker(selection: $picked, matching: .videos) {
                Label("Choose from Photos", systemImage: "photo.on.rectangle").frame(maxWidth: .infinity)
            }
            .buttonStyle(.bordered)
            .controlSize(.large)
        }
    }

    private func working(_ text: String) -> some View {
        VStack(spacing: 14) {
            ProgressView()
            Text(text)
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding(.top, 60)
    }

    private func failed(_ message: String) -> some View {
        VStack(alignment: .leading, spacing: 14) {
            Text(message).foregroundStyle(.red)
            Button("Try again") { phase = .idle }.buttonStyle(.bordered)
        }
    }

    private var settings: some View {
        NavigationStack {
            Form {
                Section("Coaching server") {
                    TextField("Address, like http://192.168.1.20:8765", text: $address)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                        .keyboardType(.URL)
                    TextField("Token", text: $token)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                }
                Section {
                    Text("Start the server on the Mac with:  python server.py\nIt prints the address and the token.")
                        .font(.footnote).foregroundStyle(.secondary)
                }
            }
            .navigationTitle("Settings")
            .toolbar { ToolbarItem(placement: .confirmationAction) { Button("Done") { showSettings = false } } }
        }
    }

    // MARK: actions

    private static func fileSize(_ url: URL) -> Int {
        let attributes = try? FileManager.default.attributesOfItem(atPath: url.path)
        return (attributes?[.size] as? Int) ?? 0
    }

    private func send(_ video: URL) {
        phase = .working("Checking the connection…")
        let client = CoachClient(address: address, token: token)
        Task {
            var upload = video
            defer { if upload != video { try? FileManager.default.removeItem(at: upload) } }
            do {
                try await client.check()
                if Self.fileSize(video) > 40_000_000 {          // large videos are shrunk first
                    phase = .working("Preparing the video…\nLong videos take a few minutes.")
                    upload = try await VideoShrinker.shrink(video)
                }
                phase = .working("Sending the video and watching your swings.\nThis takes a little while.")
                let answer = try await client.analyse(video: upload)
                phase = .result(Coaching(video: video, cues: answer.events), answer)
            } catch {
                phase = .failed(error.localizedDescription)
            }
        }
    }
}
