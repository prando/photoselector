from photoselector.privacy.reporter import FileCrashReporter, NullCrashReporter


def test_null_and_opt_in(tmp_path: object) -> None:
    NullCrashReporter().report("unused")
    path = tmp_path / "crash.log"  # type: ignore[operator]
    FileCrashReporter(path).report("boom /secret/a.jpg")
    body = path.read_text(encoding="utf-8")
    assert "/secret" not in body
    assert "boom" in body
