# MoodTunes Training Pipeline (FER2013)

This directory contains the Jupyter training notebook for training the custom MoodTunes 7-class emotion CNN model.

## Instructions

1. Download the **FER2013** dataset (contains `train` and `test` directories with `angry`, `disgust`, `fear`, `happy`, `sad`, `surprise`, `neutral`).
2. Place the dataset inside `ml/data/fer2013/`.
3. Open and run `ml/notebooks/MoodTunes_FER2013_Emotion_Training.ipynb`.
4. Upon training completion, the notebook will export:
   - `moodtunes_emotion_cnn.keras`
   - `emotion_labels.json`
   - `model_metadata.json`
5. Copy these generated files into `backend/app/models/emotion/`.
6. Update `backend/.env` to set:
   ```ini
   EMOTION_PROVIDER=moodtunes_cnn
   ```
