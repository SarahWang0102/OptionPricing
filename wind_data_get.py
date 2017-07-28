from wind_data_save import *
import datetime

def get_wind_data_pkl(evalDate):
    # 50ETF currently trading contracts
    datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
    try:
        try:
            optioncontractbasicinfo = pd.read_pickle(os.getcwd()+'\marketdata\optioncontractbasicinfo' + '.pkl')
        except:
            save_optionsinfo(evalDate)
            optioncontractbasicinfo = pd.read_pickle(os.getcwd()+'\marketdata\optioncontractbasicinfo' + '.pkl')
        optionData = optioncontractbasicinfo.values.tolist()
        optionFlds = optioncontractbasicinfo.index.tolist()
        # 50ETF market price data
        try:
            optionmkt = pd.read_pickle(os.getcwd()+'\marketdata\optionmkt_' + datestr + '.pkl')
        except FileNotFoundError:
            save_optionmkt(evalDate)
            optionmkt = pd.read_pickle(os.getcwd()+'\marketdata\optionmkt_' + datestr + '.pkl')
        mktFlds     = optionmkt.index.tolist()
        mktData     = optionmkt.values.tolist()
        # Uderlying market price
        underlyingdata = pd.read_pickle(os.getcwd() + '\marketdata\spotclose' + '.pkl')
        spot_ts  = underlyingdata.values.tolist()
        dates_ts = underlyingdata.index.tolist()
        t_temp = dates_ts[0]
        hour = t_temp.hour
        dt       = datetime.datetime(
            evalDate.year(),evalDate.month(),evalDate.dayOfMonth(),
            dates_ts[0].hour,dates_ts[0].minute,dates_ts[0].second,dates_ts[0].microsecond)
        if dt in dates_ts:
            spot     = spot_ts[dates_ts.index(dt)][0]
        else:
            print('Error: Update spot close prices from wind')
            return
        #underlying   = w.wsd("510050.SH", "close,settle", datestr, datestr, "Fill=Previous;PriceAdj=F")
        #spot  = underlying.Data[0][0]
        # Prepare strikes,maturity dates for BlackVarianceSurface
        optionids   = mktData[mktFlds.index('option_code')]
        optionids_SH = []
        for i, id in enumerate(optionids):
            id_sh = id + '.SH'
            optionids_SH.append(id_sh)
        #voldata = w.wss(optionids_SH, "us_impliedvol", "tradeDate=20170612")
        #vols = voldata.Data[0]
        vols = 0
    except:
        print('VolatilityData -- get_wind_data failed')
        return
    return vols,spot,mktData,mktFlds,optionData,optionFlds,optionids

def get_wind_data_json(evalDate):
    # 50ETF currently trading contracts
    datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
    try:
        try:
            optioncontractbasicinfo = pd.read_json(os.getcwd()+'\marketdata\optioncontractbasicinfo' + '.json')
        except:
            save_optionsinfo(evalDate)
            optioncontractbasicinfo = pd.read_json(os.getcwd()+'\marketdata\optioncontractbasicinfo' + '.json')
        optionData = optioncontractbasicinfo.values.tolist()
        optionFlds = optioncontractbasicinfo.index.tolist()
        # 50ETF market price data
        try:
            optionmkt = pd.read_json(os.getcwd()+'\marketdata\optionmkt_' + datestr + '.json')
        except:
            save_optionmkt(evalDate)
            optionmkt = pd.read_json(os.getcwd()+'\marketdata\optionmkt_' + datestr + '.json')
        mktFlds     = optionmkt.index.tolist()
        mktData     = optionmkt.values.tolist()
        # Uderlying market price
        underlyingdata = pd.read_json(os.getcwd() + '\marketdata\spotclose' + '.json')
        spot_ts  = underlyingdata.values.tolist()
        dates_ts = underlyingdata.index.tolist()
        print(evalDate.year())
        print(evalDate.month())
        print(evalDate.dayOfMonth())
        print(datetime.datetime(14,7,2017,0,0,0,500))
        print(date)
        dt       = datetime.datetime(
            evalDate.year(),evalDate.month(),evalDate.dayOfMonth(),
            dates_ts[0].hour,dates_ts[0].minute,dates_ts[0].second,dates_ts[0].microsecond)
        if dt in dates_ts:
            spot     = spot_ts[dates_ts.index(dt)][0]
        else:
            print('Error: Update spot close prices from wind')
            return
        #underlying   = w.wsd("510050.SH", "close,settle", datestr, datestr, "Fill=Previous;PriceAdj=F")
        #spot  = underlying.Data[0][0]
        # Prepare strikes,maturity dates for BlackVarianceSurface
        optionids   = mktData[mktFlds.index('option_code')]
        optionids_SH = []
        for i, id in enumerate(optionids):
            id_sh = id + '.SH'
            optionids_SH.append(id_sh)
        #voldata = w.wss(optionids_SH, "us_impliedvol", "tradeDate=20170612")
        #vols = voldata.Data[0]
        vols = 0
    except:
        print('VolatilityData -- get_wind_data failed')
        return
    return vols,spot,mktData,mktFlds,optionData,optionFlds,optionids

w.start()
#vols,spot,mktData,mktFlds,optionData,optionFlds,optionids = get_wind_data_pkl(ql.Date(14,7,2017))
vols,spot,mktData,mktFlds,optionData,optionFlds,optionids = get_wind_data_json(ql.Date(13,7,2017))