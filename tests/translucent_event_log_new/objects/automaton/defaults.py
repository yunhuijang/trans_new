from datetime import timedelta

AFREQ_THRESH = "afreq_thresh"
ATSUM_THRESH = "atsum_thresh"
ATAVG_THRESH = "atavg_thresh"
SFREQ_THRESH = "sfreq_thresh"
STSUM_THRESH = "stsum_thresh"
STAVG_THRESH = "stavg_thresh"

DEFAULT_AFREQ_THRESH = 1
DEFAULT_ATSUM_THRESH = timedelta.min
DEFAULT_ATAVG_THRESH = timedelta.min
DEFAULT_SFREQ_THRESH = 1
DEFAULT_STSUM_THRESH = timedelta.min
DEFAULT_STAVG_THRESH = timedelta.min
