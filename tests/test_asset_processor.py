from src.asset_processor import AssetProcessor

def test_asset_processor_imports():
    ap = AssetProcessor()
    assert ap is not None
