klc_find = KoreanLunarCalendar()
                    time_map_rev = {'子':'00:30 ~ 01:29 (朝子)시','丑':'01:30 ~ 03:29 (丑)시','寅':'03:30 ~ 05:29 (寅)시','卯':'05:30 ~ 07:29 (卯)시','辰':'07:30 ~ 09:29 (辰)시','巳':'09:30 ~ 11:29 (巳)시','午':'11:30 ~ 13:29 (午)시','未':'13:30 ~ 15:29 (未)시','申':'15:30 ~ 17:29 (申)시','酉':'17:30 ~ 19:29 (酉)시','戌':'19:30 ~ 21:29 (戌)시','亥':'21:30 ~ 23:29 (亥)시'}
                    
                    p_rt_val = "시간 모름"
                    if p_rt:
                        clean_rt = p_rt.replace("시", "").strip()
                        if clean_rt:
                            rt_h = K2H_JI.get(clean_rt[-1], clean_rt[-1])
                            p_rt_val = time_map_rev.get(rt_h, "시간 모름")

                    matched_list = []
                    for y in range(2050, 1800, -1):
                        klc_find.setSolarDate(y, 7, 1)
                        gj_y = klc_find.getChineseGapJaString().split()
                        if gj_y and gj_y[0][:2] == p_ry_h:
                            curr_dt = dt_mod.date(y+1, 2, 28)
                            while curr_dt >= dt_mod.date(y, 1, 1):
                                klc_find.setSolarDate(curr_dt.year, curr_dt.month, curr_dt.day)
                                gj = klc_find.getChineseGapJaString().split()
                                if len(gj) >= 3 and gj[0][:2] == p_ry_h and gj[1][:2] == p_rm_h and gj[2][:2] == p_rd_h:
                                    is_leap = getattr(klc_find, 'isIntercalary', getattr(klc_find, 'isIntercalation', False))
                                    leap_str = "윤달" if is_leap else "평달"
                                    display_str = f"양력 {curr_dt.year}년 {curr_dt.month:02d}월 {curr_dt.day:02d}일\n(음력 {klc_find.lunarYear}년 {klc_find.lunarMonth:02d}월 {klc_find.lunarDay:02d}일, {leap_str})"
                                    
                                    matched_list.append({
                                        "display": display_str,
                                        "y": curr_dt.year,
                                        "m": curr_dt.month,
                                        "d": curr_dt.day,
                                        "t": p_rt_val
                                    })
                                    break 
                                curr_dt -= dt_mod.timedelta(days=1)
                    
                    if matched_list:
