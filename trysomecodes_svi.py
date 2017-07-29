import matplotlib.pyplot as plt
import svi_calibration_utility as svi_util
import svi_prepare_vol_data as svi_data
from svi_NelderMead_optimization import  SVI_NelderMeadOptimization
import QuantLib as ql
import numpy as np
from WindPy import w


# Evaluation Settings
calendar = ql.China()
daycounter = ql.ActualActual()
evalDate = ql.Date(13,7,2017)
evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
month_indexs = svi_data.get_contract_months(evalDate)
ql.Settings.instance().evaluationDate = evalDate
# month = 0
# data =[[-0.1474550505757443, -0.12588402678393043, -0.10483765743073895, -0.08422217589933623, -0.06406353103003588, -0.04424381464711353, -0.02483149669961696, -0.005799740518179994, 0.012940699597022558, 0.031331166499017744], [0.0034992450333533667, 0.0028288432209828715, 0.0022826973487887797, 0.001562574173896798, 0.001395687015211137, 0.0011062564527481483, 0.000937295143504338, 0.0008106238480090267, 0.0006248047322452892, 0.0008217378917747827], ql.Date(26,7,2017)]

# month = 1
# data =  [[-0.08437161421518499, -0.0643466707897683, -0.044526120916894806, -0.025118556572065152, -0.005907969732817138, -0.1049962231437243, 0.012851454420562809, 0.03128297079021624], [0.003227849331359744, 0.0031802267838396585, 0.0030925895644418762, 0.0030709180254420458, 0.0030059546678610806, 0.003399860964614313, 0.002857160133643782, 0.0029170391547165913], ql.Date(23,8,2017)]

# month = 2
#data =[[-0.17043700149516153, -0.1480800039139724, -0.1269216324334573, -0.10558166561707674, -0.0849819350025284, -0.06447321964498587, -0.1926903988421557, -0.04496035968314911, -0.02559532463676001, -0.006036382122508532, 0.012428995993457544, 0.031084804125535295], [0.00845234024433896, 0.0074060422025051, 0.00684338521040316, 0.006353501369090554, 0.005930760216888737, 0.005454778410052806, 0.009315103522331631, 0.005749869750751505, 0.005567190436424295, 0.0053004694217071565, 0.00482120655982343, 0.005227916195028757], ql.Date(27,9,2017)]
# month = 3
data = [[-0.17020673945007952, -0.14785999239882358, -0.1259589277431486, -0.10494363189886617, -0.08448331254457994, -0.193336342189172, -0.06315303679724402, -0.04289427262697295, -0.0233070377401115, -0.003680225706168828, 0.014864178978808422, 0.033289553177048986], [0.014913554184199311, 0.013893843398397259, 0.013346833402365796, 0.012804059733159892, 0.01218861887847, 0.016093845190278972, 0.01172065969354381, 0.01116028753695756, 0.011065580471748743, 0.01070002305128101, 0.012290592334057276, 0.01208676159804692], ql.Date(27,12,2017)]

for i in range(10):
    print('data_for_optimiztion : ', data)
    logMoneynesses  = data[0]
    totalvariance   = data[1]
    expiration_date = data[2]
    print('expiration date: ',expiration_date)
    ## NelderMeadOptimization
    #nm   = SVI_NelderMeadOptimization(data, init_adc = [0.5,0.5,0.5], init_msigma = [1,1])
    nm   = SVI_NelderMeadOptimization(data)
    params,obj = nm.optimization()
    _a_star, _d_star, _c_star, m_star, sigma_star = params
    x_svi  = np.arange(min(logMoneynesses)-0.05, max(logMoneynesses)+0.05, 0.1 / 100)  # log_forward_moneyness
    y_svi  = np.divide((x_svi - m_star), sigma_star)
    tv_svi = _a_star + _d_star * y_svi + _c_star * np.sqrt(y_svi**2 + 1)  # totalvariance objective fution values
    print('_a_star, _d_star, _c_star, m_star, sigma_star',_a_star, _d_star, _c_star, m_star, sigma_star)
    ########################################################################################################################
    ## Get a,b,rho
    ttm = daycounter.yearFraction(evalDate, expiration_date)
    a_star = np.divide(_a_star, ttm)
    b_star = np.divide(_c_star, (sigma_star * ttm))
    rho_star = np.divide(_d_star, _c_star)
    tv_svi2 = np.multiply(a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)), ttm)
    print('a_star,b_star,rho_star, m_star, sigma_star : ',a_star,b_star,rho_star, m_star, sigma_star)
    ########################################################################################################################
    # plot input data -- moneyness-totalvariance
    plt.figure(i)
    plt.plot(logMoneynesses, totalvariance, 'ro')

    ########################################################################################################################
    # Plot SVI volatility smile -- moneyness-totalvariance
    plt.plot(x_svi, tv_svi, 'b--')
    t = str( daycounter.yearFraction(evalDate,expiration_date))
    plt.title('SVI total variance, T = ' + t)
plt.show()