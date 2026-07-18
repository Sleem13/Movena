from pathlib import Path


def test_squat_upload_log_does_not_include_source_filename():
    source = Path("backend/app/api/routes/squat_analysis.py").read_text(encoding="utf-8")

    assert 'logger.info("Video received: filename=%s' not in source
    assert 'logger.info("Video upload received: content_type=%s"' in source
