import pandas as pd

benigno = pd.read_csv("../data/test/Benign_IoT_Traffic_00003_20251203170328.csv")
syn = pd.read_csv("../data/test/SYN_FLOOD_op2__00002_20251211101006.csv")
icmp = pd.read_csv("../data/test/ICMP_FLOOD_op5__00001_20251212102824.csv")
toniot = pd.read_csv('../data/toniot.csv')

toniot.columns = (
        toniot.columns
        .str.strip()
        .str.lower()
    )
df_1 = toniot[toniot['label'] == 1]
df_0 = toniot[toniot['label'] == 0]

muestra_1 = df_1.sample(n=52338, random_state=42)
muestra_0 = df_0.sample(n=22360, random_state=42)

test = pd.concat([muestra_1, muestra_0])
train = toniot.drop(test.index)

test = pd.concat([test, benigno])
test = pd.concat([test, syn])
test = pd.concat([test, icmp])
test = test.sample(frac=1, random_state=42)

train.to_csv('../data/toniot_train.csv', index=False)
test.to_csv('../../dos_detector/web_app/data/test_data.csv', index=False)

print(f'Filas train: {len(train)}')
print(f'Filas test: {len(test)}')