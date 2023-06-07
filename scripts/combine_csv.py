import sys
import pandas as pd
from glob import glob

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print('Requires 2 arguments "<input files (wildcard)>" <output file>')
        sys.exit(-1)
    else:
        input_files = sys.argv[1]
        output_file = sys.argv[2]
    
    print(f'Input files: {input_files}, Output file: {output_file}')
    adf = None

    for i, fn in enumerate(sorted(glob(input_files))):
        if i % 1000 == 0:
            print(i, fn)
        df = pd.read_csv(fn)
        adf = df if adf is None else pd.concat([adf, df], ignore_index=True)
        #if i > 10:
        #    break
    print(f'Saving to file...({output_file})')
    adf.to_csv(output_file, index=False)
