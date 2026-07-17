def test_training_tracks_are_separate_and_experimental():
 text=open("docs/ml_dl_training_tracks.md",encoding="utf-8").read().lower();assert "video pose" in text and "skeleton sequence" in text and "sensor time-series" in text;assert "do not blindly merge" in text and "experimental" in text
