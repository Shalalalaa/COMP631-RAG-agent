from transformers import pipeline

# 初始化
emotion_model = pipeline("text-classification", model="nateraw/bert-base-uncased-emotion", return_all_scores=True)

def detect_emotions(text, top_n=2):
    scores = emotion_model(text)[0]
    sorted_scores = sorted(scores, key=lambda x: x['score'], reverse=True)
    return [e['label'] for e in sorted_scores[:top_n]]
