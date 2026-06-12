"""Shared constants for the HandOsteo pipeline."""

ALLOWED_MODALITIES = ("CR", "DX")
SUPPORTED_VIEWS = ("AP", "PA")

# MCP classification thresholds (%)
# DXA-validated cut-points from Schreiber et al. (2017), J Hand Surg Am
# 42(4):e272-e279, doi:10.1016/j.jhsa.2017.01.012 (PMID 28242242):
#   <60 % optimised sensitivity/specificity for osteopenia vs normal
#   <50 % optimised sensitivity/specificity for osteoporosis vs normal
# Original radiogrammetry method: Barnett & Nordin (1960), Clin Radiol
# 11:166-174, doi:10.1016/S0009-9260(60)80012-8.
MCP_NORMAL_THRESHOLD = 60.0      # MCP >= 60 % → normal bone density
MCP_OSTEOPENIA_THRESHOLD = 50.0  # 50 % <= MCP < 60 % → osteopenia
                                  # MCP < 50 % → osteoporosis