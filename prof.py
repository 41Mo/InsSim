import sys, os
import pstats
from pstats import SortKey

ps = pstats.Stats("./profile")

ps.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(.3)  # plink around with this to get the results you need
