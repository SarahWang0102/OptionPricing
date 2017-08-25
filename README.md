OptionPricing - Research on OTC options pricing models

=======================================================================================================================
 1. SVI MODEL
=======================================================================================================================

 step 1. DATA PREPARATION :

 Prepare option data for optimization, using call options/put options/call & put combined by put call parity
 adjusted rates.

 Utilities functions in svi_prepare_vol_data.py


 step 2. MODEL CALIBRATION :

 Use Quasi-Explicit Optimization (Nelder-Mead Simplex Algorithm) to calibrate model parameters.

 Run svi_calibration_params_opt_XXX.py (XXX stands for different dataset in step 1)


 step 3. INSAMPLE PERFORMANCE:

 Insample pricing error analysis.

 Run insample_performance_svi_put.py


 step 4. DYNYMIC HEDGE PERFORMANCE:

 Dynamic hedge using t-2 calibrated params and t-1 delta to calculate t date hedge error.Hedge could be based on
 smoothed implied volatility curve (3-day or 5-day) or original ones.

 Run hedging_performance_svi_XXX.py (XXX stands for methods and dataset call/put)

