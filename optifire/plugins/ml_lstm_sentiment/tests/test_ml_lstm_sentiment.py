import pytest
from ml_lstm_sentiment.impl import MlLstmSentiment

@pytest.mark.asyncio
async def test_run():
    plugin = MlLstmSentiment()
    from optifire.plugins import PluginContext
    result = await plugin.run(PluginContext(params={}))
    assert result.success
