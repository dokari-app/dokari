import AVKit
import SwiftUI

/// The result of one video: the player with captions, what was said, and every swing. Its own view so the captions refresh as the video plays.
struct ResultView: View {
    @ObservedObject var coaching: Coaching
    let answer: CoachAnswer
    var onDone: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            ZStack(alignment: .bottom) {
                VideoPlayer(player: coaching.player)
                    .aspectRatio(9.0 / 16.0, contentMode: .fit)
                    .frame(maxHeight: 460)
                    .clipShape(RoundedRectangle(cornerRadius: 16))
                if !coaching.caption.isEmpty {
                    Text(coaching.caption)
                        .font(.body)
                        .foregroundStyle(.white)
                        .padding(10)
                        .background(.black.opacity(0.72), in: RoundedRectangle(cornerRadius: 12))
                        .padding(10)
                        .padding(.bottom, 44)
                        .allowsHitTesting(false)
                }
            }
            summary(answer)
            Text("WHAT WAS SAID").font(.caption).foregroundStyle(.secondary)
            if answer.events.isEmpty {
                Text("Nothing needed saying. No habit repeated often enough to be worth interrupting.")
                    .foregroundStyle(.secondary)
            }
            ForEach(answer.events) { cue in
                Button { coaching.seek(to: cue.t) } label: {
                    HStack(alignment: .top, spacing: 12) {
                        Text(clock(cue.t)).monospacedDigit().foregroundStyle(.secondary).frame(width: 44, alignment: .leading)
                        VStack(alignment: .leading, spacing: 2) {
                            Text(cue.kind.uppercased()).font(.caption2).foregroundStyle(.secondary)
                            Text(cue.text).multilineTextAlignment(.leading)
                        }
                    }
                }
                .buttonStyle(.plain)
                Divider()
            }
            DisclosureGroup("Every swing (\(answer.attempts.count))") {
                ForEach(answer.attempts) { a in
                    Button { coaching.seek(to: a.start) } label: {
                        HStack(alignment: .top, spacing: 12) {
                            Text(clock(a.start)).monospacedDigit().foregroundStyle(.secondary).frame(width: 44, alignment: .leading)
                            VStack(alignment: .leading, spacing: 2) {
                                Text(name(a.activity).uppercased()).font(.caption2).foregroundStyle(.secondary)
                                Text(a.missed.isEmpty ? "nothing flagged" : a.missed.joined(separator: ", "))
                                    .foregroundStyle(a.missed.isEmpty ? Color.primary : Color.orange)
                                    .multilineTextAlignment(.leading)
                            }
                        }
                    }
                    .buttonStyle(.plain)
                    .padding(.vertical, 6)
                }
            }
            Button("Another video") {
                coaching.stop()
                onDone()
            }
            .buttonStyle(.bordered)
        }
    }

    private func summary(_ answer: CoachAnswer) -> some View {
        var counts: [String: Int] = [:]
        for a in answer.attempts { counts[name(a.activity), default: 0] += 1 }
        return HStack(alignment: .top, spacing: 24) {
            ForEach(counts.sorted { $0.key < $1.key }, id: \.key) { key, n in
                VStack(alignment: .leading) {
                    Text("\(n)").font(.title.bold())
                    Text(n == 1 ? key : key + "s").font(.footnote).foregroundStyle(.secondary)
                }
            }
            VStack(alignment: .leading) {
                Text("\(answer.events.count)").font(.title.bold())
                Text("said").font(.footnote).foregroundStyle(.secondary)
            }
        }
    }

    private func name(_ activity: String?) -> String {
        (activity ?? "swing").replacingOccurrences(of: "tennis_", with: "").replacingOccurrences(of: "_", with: " ")
    }

    private func clock(_ t: Double) -> String {
        let s = Int(t.rounded())
        return "\(s / 60):" + String(format: "%02d", s % 60)
    }
}
