# Waste classifier model

By default EcoTrack AI uses **MobileNetV2 pretrained on ImageNet** and maps its labels to the three
waste categories (`modules/ai_classifier.py`). This works for common items (bottles, fruit, phones,
keyboards) but ImageNet has no "banana peel" or "battery" class, so accuracy on real waste is limited.

## Use your own trained model
1. Collect images in `dataset/train/<Category>/` and `dataset/val/<Category>/` for
   `Biodegradable`, `Dry Recyclable`, `Hazardous / E-Waste` (e.g. TrashNet / TACO / your own photos).
2. Run `python models/waste_classifier/train_classifier.py --data dataset`.
3. It writes `model.keras` and `labels.json` here; the app detects them automatically.
