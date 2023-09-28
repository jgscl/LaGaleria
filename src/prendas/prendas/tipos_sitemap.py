import re
import json

from datetime import datetime


def analizador_sitemap():
    f = open('/home/j/Downloads/sitemap-es-es.xml')
    lineas = f.readlines()

    daily_otras = 0
    daily_l = 0
    daily_mkt = 0
    daily_help = 0
    weekly_look = 0
    weekly_p = 0
    weekly_pT = 0
    weekly_pG = 0
    weekly_otras = 0
    for linea in lineas:
        daily_reg_otras = re.search('^<url> <loc>(?!.*(/help|-mkt[0-9]+|-l[0-9]+)).*<changefreq>daily</changefreq>.*</url>$', linea)
        daily_reg_help = re.search('^<url> <loc>(?!.*(-mkt[0-9]+|-l[0-9]+)).*<changefreq>daily</changefreq>.*</url>$', linea) 
        daily_reg_l = re.search('^<url> <loc>(?!.*(/help|-mkt[0-9]+)).*<changefreq>daily</changefreq>.*</url>$', linea)
        daily_reg_mkt = re.search('^<url> <loc>(?!.*(/help|-l[0-9]+)).*<changefreq>daily</changefreq>.*</url>$', linea)
        weekly_reg_otras = re.search('^<url> <loc>(?!.*(/look|-pG[0-9]+|-pT[0-9]+|-p[0-9]+)).*<changefreq>weekly</changefreq>.*</url>$', linea)
        weekly_reg_p = re.search('^<url> <loc>(?!.*(/look|-pG[0-9]+|-pT[0-9]+)).*<changefreq>weekly</changefreq>.*</url>$', linea)
        weekly_reg_look = re.search('^<url> <loc>.*(/look).*<changefreq>weekly</changefreq>.*</url>$', linea)
        weekly_reg_pG = re.search('^<url> <loc>(?!.*(/look|-pT[0-9]+|-p[0-9]+)).*<changefreq>weekly</changefreq>.*</url>$', linea)
        weekly_reg_pT = re.search('^<url> <loc>(?!.*(/look|-pG[0-9]+|-p[0-9]+)).*<changefreq>weekly</changefreq>.*</url>$', linea)
        
        """Contar el número de urls tipo daily"""
        if daily_reg_otras is not None:
            print(daily_reg_otras.group())
            daily_otras += 1
        if daily_reg_l is not None:
            #print(daily_reg_l.group())
            daily_l += 1
        if daily_reg_mkt is not None:
            #print(daily_reg_mkt.group())
            daily_mkt += 1
        if daily_reg_help is not None:
            #print(dailY_reg_help.group())
            daily_help += 1
        
        """Contar el número de urls tipo weekly"""
        if weekly_reg_otras is not None:
            #print(weekly_reg_otras.group())
            weekly_otras += 1
        if weekly_reg_look is not None:
            #print(weekly_reg_look.group())
            weekly_look += 1
        if weekly_reg_pT is not None:
            #print(weekly_reg_pT.group())
            weekly_pT += 1
        if weekly_reg_pG is not None:
            #print(weekly_reg_pG.group())
            weekly_pG += 1 
        if weekly_reg_p is not None:
            #print(weekly_reg_p.group())
            weekly_p += 1
        
    print("TIPO DAILY")
    final_help = daily_help - daily_otras
    print("- Tipo /help:", final_help)
    final_l = daily_l - daily_otras
    print("- Tipo -l[0-9]+:", final_l)
    final_mkt = daily_mkt - daily_otras
    print("- Tipo -mkt[0-9]+:", final_mkt)
    final_daily_otros = daily_otras
    print("- Otros:", final_daily_otros)
    final_daily = final_help + final_l + final_mkt + final_daily_otros
    print("Total:", str(final_daily))

    print("\nTIPO WEEKLY")
    final_look = weekly_look - weekly_otras
    print("- Tipo /look:", final_look)
    final_p = weekly_p - weekly_otras
    print("- Tipo -p[0-9]+:", final_p)
    final_pT = weekly_pT - weekly_otras
    print("- Tipo -pT[0-9]+:", final_pT)
    final_pG = weekly_pG - weekly_otras
    print("- Tipo -pG[0-9]+:", final_pG)
    final_weekly_otros = weekly_otras
    print("- Otros:", weekly_otras)
    final_weekly = final_look + final_p + final_pT + final_pG + final_weekly_otros
    print("Total:", str(final_weekly))

    print("\nTotal WEEKLY y DAILY:", str(final_weekly + final_daily))
    

analizador_sitemap()

