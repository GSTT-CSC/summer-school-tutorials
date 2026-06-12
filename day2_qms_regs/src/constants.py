"""Shared constants for the HandOsteo pipeline."""

ALLOWED_MODALITIES = ("CR", "DX")
SUPPORTED_VIEWS = ("AP", "PA")

# MCP classification thresholds (%)
MCP_NORMAL_THRESHOLD = 75.0      # MCP >= 75 % → normal bone density
MCP_OSTEOPENIA_THRESHOLD = 65.0  # 65 % <= MCP < 75 % → osteopenia
                                  # MCP < 65 % → osteoporosis