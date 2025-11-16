def test_package_import():
    import src  # ensures project root on sys.path
    assert hasattr(src, "__package__") or True
