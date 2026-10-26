import AVFoundation
import SwiftUI

/// Plays the video and says the cues at their moments: the caption appears, and the phone speaks it.
@MainActor
final class Coaching: ObservableObject {
    let player: AVPlayer
    let cues: [CoachAnswer.Cue]
    @Published var caption = ""

    private var next = 0
    private var captionUntil = 0.0
    private var observer: Any?
    private let voice = AVSpeechSynthesizer()

    init(video: URL, cues: [CoachAnswer.Cue]) {
        player = AVPlayer(url: video)
        self.cues = cues.sorted { $0.t < $1.t }
        let session = AVAudioSession.sharedInstance()
        try? session.setCategory(.playback, mode: .moviePlayback)
        try? session.setActive(true)
        observer = player.addPeriodicTimeObserver(forInterval: CMTime(seconds: 0.1, preferredTimescale: 600), queue: .main) { [weak self] time in
            MainActor.assumeIsolated { self?.tick(time.seconds) }
        }
    }

    func stop() {
        player.pause()
        voice.stopSpeaking(at: .immediate)
        if let observer { player.removeTimeObserver(observer) }
        observer = nil
    }

    func seek(to seconds: Double) {
        voice.stopSpeaking(at: .immediate)
        caption = ""
        next = cues.firstIndex { $0.t >= seconds } ?? cues.count
        player.seek(to: CMTime(seconds: max(0, seconds - 0.5), preferredTimescale: 600), toleranceBefore: .zero, toleranceAfter: .zero)
        player.play()
    }

    private func tick(_ t: Double) {
        if next > 0, t < cues[next - 1].t - 0.3 {               // the viewer went back: the cues can be said again
            next = cues.firstIndex { $0.t >= t } ?? cues.count
        }
        while next < cues.count, cues[next].t <= t {
            let cue = cues[next]
            next += 1
            if t - cue.t < 1.5 { say(cue) }
        }
        if t > captionUntil { caption = "" }
    }

    private func say(_ cue: CoachAnswer.Cue) {
        caption = cue.text
        captionUntil = cue.t + 4.5
        guard cue.kind != "principle" else { return }          // the long "why" is read, not spoken
        voice.stopSpeaking(at: .immediate)
        let utterance = AVSpeechUtterance(string: cue.text)
        utterance.rate = AVSpeechUtteranceDefaultSpeechRate
        voice.speak(utterance)
    }
}
