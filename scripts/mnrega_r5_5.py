#!/usr/bin/env python
# coding: utf-8

import sys
import os
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd

state_codes = {
'01': 'ANDAMAN AND NICOBAR',
'02': 'ANDHRA PRADESH',
'03': 'ARUNACHAL PRADESH',
'04': 'ASSAM',
'05': 'BIHAR',
'33': 'CHHATTISGARH',
'07': 'DN HAVELI AND DD',
'10': 'GOA',
'11': 'GUJARAT',
'12': 'HARYANA',
'13': 'HIMACHAL PRADESH',
'14': 'JAMMU AND KASHMIR',
'34': 'JHARKHAND',
'15': 'KARNATAKA',
'16': 'KERALA',
'37': 'LADAKH',
'19': 'LAKSHADWEEP',
'17': 'MADHYA PRADESH',
'18': 'MAHARASHTRA',
'20': 'MANIPUR',
'21': 'MEGHALAYA',
'22': 'MIZORAM',
'23': 'NAGALAND',
'24': 'ODISHA',
'25': 'PUDUCHERRY',
'26': 'PUNJAB',
'27': 'RAJASTHAN',
'28': 'SIKKIM',
'29': 'TAMIL NADU',
'36': 'TELANGANA',
'30': 'TRIPURA',
'31': 'UTTAR PRADESH',
'35': 'UTTARAKHAND',
'32': 'WEST BENGAL'
}

def clean_and_save_csv(df, fn, xc=0):
    bfn = os.path.basename(fn)
    xcols = list(df.columns[-xc:]) if xc != 0 else []
    new_labels = pd.MultiIndex.from_frame(df.iloc[:5].T.astype(str), names=['', '', '', '', ''])
    df = df.set_axis(new_labels, axis=1).iloc[3:]
    df.reset_index(drop=True, inplace=True)
    # flatten columns
    flat_cols = []
    pcols = df.columns.values[:-xc] if xc != 0 else df.columns.values
    for cols in pcols:
        new_cols = []
        for c in cols[:-1]:
            c = c.replace('*', '').strip()
            if c not in new_cols:
                new_cols.append(c)
        flat_cols.append('|'.join(new_cols))
    flat_cols += xcols

    df.columns = flat_cols

    df.drop(df.head(1).index,inplace=True) # drop first n rows
    df.drop(df.tail(1).index,inplace=True) # drop last n rows
    
    df.to_csv(fn, index=False)


if __name__ == '__main__':

    if len(sys.argv) > 1:
        year = int(sys.argv[1])
        print(f"The year entered is: {year}")
    else:
        print("Please provide a year as a command line argument.")
        sys.exit(-1)

    outdir = f'{year}-csv/'

    # Check if the directory exists
    if not os.path.exists(outdir):
        # Create the directory
        os.makedirs(outdir)
        print(f"Directory '{outdir}' created.")
    else:
        print(f"Directory '{outdir}' already exists.")

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    s = requests.Session()

    if False:
        r0 = s.get(f'https://nreganarep.nic.in/netnrega/state_html/empstatusnewall_scst.aspx?lflag=eng&fin_year={year}-{year + 1}&source=national&labels=labels&Digest=2sK2jsi9G7FHeqD/Cv4G1Q', headers=headers)

        if r0.status_code != 200:
            print(f'Error to get start URL with status code: {r0.status_code}')
            sys.exit(-1)
        dfs = pd.read_html(r0.content, encoding='utf-8')
        df = dfs[4]
        clean_and_save_csv(df, f'{year}-csv/r5_5_states.csv')
        soup = BeautifulSoup(r0.content, 'lxml')
        states = []
        for l in soup.find_all('a', {'href': re.compile('empstatusnewall_scst\.aspx.*')}):
            states.append((l.text, l['href']))

    states = []
    for code in state_codes:
        name = state_codes[code]
        states.append((name, f'empstatusnewall_scst.aspx?page=S&lflag=eng&state_name={name}&state_code={code}&fin_year={year}-{year + 1}&source=national&Digest=ih7D13FrF5jIKF4VpGrngQ'))

    for state, href in states:
        print('- State:', state)
        url = 'https://nreganarep.nic.in/netnrega/state_html/' + href
        #print(url)
        try:
            r1 = s.get(url, headers=headers, timeout=5)
            if r1.status_code != 200:
                print(f'Error to get start URL with status code: {r1.status_code}')
                continue
        except Exception as e:
            print(url)
            continue
        try:
            dfs = pd.read_html(r1.content, encoding='utf-8')
            df = dfs[4]
            df['state'] = state
            clean_and_save_csv(df, f'{year}-csv/r5_5_district_{state}.csv', 1)
            soup2 = BeautifulSoup(r1.content, 'lxml')
            districts = []
            for l in soup2.find_all('a', {'href': re.compile('empstatusnewall_scst\.aspx.*')}):
                districts.append((l.text, l['href']))
            for dt in districts:
                district = dt[0].strip()
                print('  - District:', district)
                url = 'https://nreganarep.nic.in/netnrega/state_html/' + dt[1]
                r3 = s.get(url, headers=headers)
                if r3.status_code == 200:
                    try:
                        dfs = pd.read_html(r3.content, encoding='utf-8')
                        df = dfs[4]
                        df['state'] = state
                        df['district'] = district
                        clean_and_save_csv(df, f'{year}-csv/r5_5_block_{district}+{state}.csv', 2)
                        soup3 = BeautifulSoup(r3.content, 'lxml')
                        blocks = []
                        for l in soup3.find_all('a', {'href': re.compile('empstatusnewall_scst\.aspx.*')}):
                            blocks.append((l.text, l['href']))
                        for bl in blocks:
                            block = bl[0].strip()
                            print('    - Block:', block)
                            if block.find('/') == -1:
                                continue
                            block = block.replace('/', '_')
                            url = 'https://nreganarep.nic.in/netnrega/state_html/' + bl[1]
                            r4 = s.get(url, headers=headers)
                            if r4.status_code == 200:
                                try:
                                    dfs = pd.read_html(r4.content, encoding='utf-8')
                                    df = dfs[4]
                                    df['state'] = state
                                    df['district'] = district
                                    df['block'] = block
                                    clean_and_save_csv(df, f'{year}-csv/r5_5_panchayat_{block}+{district}+{state}.csv', 3)
                                except Exception as e:
                                    print('ERROR', e)
                            else:
                                print('Block ERROR', r4.status_code, block)
                            #break
                    except Exception as e:
                        print('ERROR:', e)
                else:
                    print('District ERROR', r3.status_code, district)
                #break
        except Exception as e:
            print('ERROR:', e)
        #break
