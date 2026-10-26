import SwiftUI
import UIKit

/// The system camera, set to video. Hands back a copy of the recording that stays on disk.
struct CameraRecorder: UIViewControllerRepresentable {
    var onFinish: (URL?) -> Void

    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.sourceType = .camera
        picker.mediaTypes = ["public.movie"]
        picker.cameraCaptureMode = .video
        picker.videoQuality = .typeHigh
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_ controller: UIImagePickerController, context: Context) {}

    func makeCoordinator() -> Coordinator { Coordinator(onFinish: onFinish) }

    final class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let onFinish: (URL?) -> Void
        init(onFinish: @escaping (URL?) -> Void) { self.onFinish = onFinish }

        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
            guard let source = info[.mediaURL] as? URL else { onFinish(nil); return }
            let copy = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString + ".mov")
            try? FileManager.default.copyItem(at: source, to: copy)
            onFinish(FileManager.default.fileExists(atPath: copy.path) ? copy : nil)
        }

        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) { onFinish(nil) }
    }
}
