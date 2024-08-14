#%%
from pyedgarai.pyedgarai import get_submission_history
from pyedgarai.objects import df_from_dict_singletons
import time

# test get_submission_history for AAPL
cik = 320193

dict_ = get_submission_history(cik)
df = df_from_dict_singletons(dict_)

# %%
