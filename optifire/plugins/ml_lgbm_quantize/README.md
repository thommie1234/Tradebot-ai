# ml_lgbm_quantize

**Category:** ml

## Description

LightGBM quantization

## Status

🟡 **STUB IMPLEMENTATION** - This plugin is scaffolded but requires full implementation.

## Configuration

Edit `plugins/ml_lgbm_quantize/plugin.yaml` to configure:

- **enabled**: Set to `true` to activate
- **schedule**: When to run (cron, @idle, @open, @close, interval_Xs)
- **budget**: Resource limits (cpu_ms, mem_mb)

## Usage

Enable in `configs/features.yaml`:

```yaml
plugins:
  ml_lgbm_quantize:
    enabled: true
    schedule: "@idle"
    budget:
      cpu_ms: 1000
      mem_mb: 50
```

## Inputs

- market_data
- features

## Outputs

- signals
- features
- metrics

## Resource Requirements

- **CPU**: ~500ms per run
- **Memory**: ~30 MB
- **Disk**: Minimal

## Safety Notes

- Plugin is OFF by default
- Enable only after reviewing implementation
- Monitor resource usage in diagnostics dashboard
- Can be toggled at runtime via API

## Development

To implement full logic:

1. Edit `impl.py` and replace stub in `run()` method
2. Add required dependencies to `plugin.yaml`
3. Write comprehensive tests
4. Test resource usage against budget
5. Update this README with actual behavior

## License

Part of OptiFIRE trading system.
