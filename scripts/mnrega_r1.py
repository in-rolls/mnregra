#!/usr/bin/env python
# coding: utf-8

import sys
import os
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd


def clean_and_save_csv(df, fn):
    bfn = os.path.basename(fn)
    if bfn.startswith('r1_state'):
        xc = 0
    elif bfn.startswith('r1_district'):
        xc = 1
    elif bfn.startswith('r1_block'):
        xc = 2
    elif bfn.startswith('r1_panchayat'):
        xc = 3
    xcols = list(df.columns[-xc:]) if xc != 0 else []
    new_labels = pd.MultiIndex.from_frame(df.iloc[:3].T.astype(str), names=['', '', ''])
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

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    s = requests.Session()

    r1 = s.get(f'https://nreganarep.nic.in/netnrega/app_issue.aspx?lflag=eng&fin_year={year}-{year + 1}&source=national&labels=labels&Digest=HNrisV4bhHnb7Gve3mAKYQ', headers=headers)
    if r1.status_code != 200:
        print(f'Error to get start URL with status code: {r1.status_code}')
        sys.exit(-1)

    dfs = pd.read_html(r1.content, encoding='utf-8')
    df = dfs[6]
    clean_and_save_csv(df, 'csv/r1_state.csv')

    soup1 = BeautifulSoup(r1.content, 'lxml')
    states = []
    for l in soup1.find_all('a', {'href': re.compile('app_issue\.aspx.*')}):
        print(l.text)
        states.append((l.text, l['href']))
    print(f'Number of state: {len(states)}')

    for st in states:
        state = st[0].strip()
        print('- State:', state)

        url = 'https://nreganarep.nic.in/netnrega/' + st[1]
        r2 = s.get(url, headers=headers)
        if r2.status_code == 200:
            try:
                dfs = pd.read_html(r2.content, encoding='utf-8')
                df = dfs[6]
                df['state'] = state
                clean_and_save_csv(df, 'csv/r1_district_{0:s}.csv'.format(state))
                soup2 = BeautifulSoup(r2.content, 'lxml')
                districts = []
                for l in soup2.find_all('a', {'href': re.compile('app_issue\.aspx.*')}):
                    districts.append((l.text, l['href']))
                for dt in districts:
                    district = dt[0].strip()
                    print('  - District:', district)
                    url = 'https://nreganarep.nic.in/netnrega/' + dt[1]
                    r3 = s.get(url, headers=headers)
                    if r3.status_code == 200:
                        try:
                            dfs = pd.read_html(r3.content, encoding='utf-8')
                            df = dfs[6]
                            df['state'] = state
                            df['district'] = district
                            clean_and_save_csv(df, 'csv/r1_block_{0:s}+{1:s}.csv'.format(district, state))
                            soup3 = BeautifulSoup(r3.content, 'lxml')
                            blocks = []
                            for l in soup3.find_all('a', {'href': re.compile('app_issue\.aspx.*')}):
                                blocks.append((l.text, l['href']))
                            for bl in blocks:
                                block = bl[0].strip()
                                print('    - Block:', block)
                                url = 'https://nreganarep.nic.in/netnrega/' + bl[1]
                                r4 = s.get(url, headers=headers)
                                if r4.status_code == 200:
                                    try:
                                        dfs = pd.read_html(r4.content, encoding='utf-8')
                                        df = dfs[6]
                                        df['state'] = state
                                        df['district'] = district
                                        df['block'] = block
                                        clean_and_save_csv(df, 'csv/r1_panchayat_{0:s}+{1:s}+{2:s}.csv'.format(block, district, state))
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
        else:
            print('State ERROR', r2.status_code, state)
        #break
