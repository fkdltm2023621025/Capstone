import pandas as pd

# CSV 파일 경로
csv_file_path = 'users.csv'

# CSV 파일 읽기
df = pd.read_csv(csv_file_path)

# 테이블 이름
table_name = 'flagship'

# 컬럼 이름 가져오기
columns = df.columns.tolist()

# `INSERT` 문 생성
insert_statements = []

for index, row in df.iterrows():
    values = [f"'{str(value)}'" for value in row.values]
    insert_statement = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});"
    insert_statements.append(insert_statement)

# 생성된 `INSERT` 문 출력
for statement in insert_statements:
    print(statement)
