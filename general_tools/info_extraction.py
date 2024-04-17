with open("./data.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

def line_content_spliter(content: str):
    content_list = content.replace(" ", "").replace("\n", "").replace("\r", "").split("\t")
    if len(content_list) == 1:
        return []
    return content_list

table_columns = line_content_spliter(lines[0])[1:]

pairs = []
for line in lines[1:]:
    line_content = line_content_spliter(line)
    if line_content:
        row_name = line_content[0]
        row_values = line_content[1:]
        for idx, value_str in enumerate(row_values):
            value = int(value_str)
            if value >= 2:
                pairs.append((row_name, table_columns[idx]))

write_content = "\n".join([
    x[0] + "\tBoway,BowayProcess,SmeltingPhase3\t" + x[1] + "\tBoway,BowayMgmt,QualityDefect"
    for x in pairs
])

with open("extracted.txt", "w", encoding="utf-8") as f:
    f.write(write_content)