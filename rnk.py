import numpy as np
import pandas as pd
import re

def le_100(x):
    return 5000 - (x - 1) * 6

def le_200(x):
    return le_100(100) - (x - 100) * 5

def le_300(x):
    return le_200(200) - (x - 200) * 4

def le_500(x):
    return le_300(300) - (x - 300) * 3

def le_800(x):
    return le_500(500) - (x - 500) * 2

def gt_800(x):
    return le_800(800) - (x - 800) * 1

def get_point(x):
    if x > 0:
        if x <= 100:
            return le_100(x)
        elif x <= 200:
            return le_200(x)
        elif x <= 300:
            return le_300(x)
        elif x <= 500:
            return le_500(x)
        elif x <= 800:
            return le_800(x)
        elif x > 800:
            return gt_800(x)
    else:
        return


def rank(csv_file, classes_counts, field):
    df = pd.read_csv(csv_file)
     
    df['rank'] = df[field].rank(method='max', ascending=False)
    
    

    df['point'] = df['rank'].apply(get_point)
    
    
    
    df.sort_values(['class',field],ascending=[1,0],inplace=True)
    grouped = pd.DataFrame([])

    for k,v in classes_counts.items():
       group_ = df[df['class']==k].groupby(['class']).head(v)
       grouped = pd.concat([grouped, group_])

    result = grouped.groupby('class').mean().sort_values(by='point', ascending=False)
    count = grouped.groupby('class').count()['sn']
    result = result.apply(lambda x: round(x, 2))
    result['count'] = count
    res_point = result.to_dict(orient='list')['point']
    res_count = result.to_dict(orient='list')['count']
    res_class = result.index.to_list()
    
    res = pd.DataFrame({'class':res_class, 'point': res_point, 'count': res_count})
    return res 

def rank_all(csv_file, classes_counts, score_names, sort_by='score_total'):
	aod = []
	for score_name in score_names:
		res_ = rank(csv_file, classes_counts, score_name)
		point_name = re.sub(r'score_','point_',score_name)
		
		df_ = pd.DataFrame({'class':res_['class'], point_name:res_['point']})
		
		if 'dfs' in locals().keys():
			dfs = pd.merge(dfs, df_, on='class')
		else:
		    dfs = df_
	sort_name = re.sub(r'score_','point_',sort_by)
	dfs_sorted = dfs.sort_values(by=sort_name, ascending=False)
	cols = list(dfs_sorted)
	cols.insert(1, cols.pop(cols.index(sort_name)))
	return dfs_sorted[cols]

def rank_whole(csv_file, classes_counts, score_names):
    for score_name in score_names:
        res_ = rank(csv_file, classes_counts, score_name)
        rank_name = re.sub(r'score_','rank_',score_name)
        point_name = re.sub(r'score_','point_',score_name)
        df_ = pd.DataFrame({rank_name:res_['class'], point_name:res_['point']})
        if 'dfs' in locals().keys():
            dfs = pd.concat([dfs, df_], axis=1)
        else:
            dfs = df_
        
    return dfs

if __name__ == "__main__":
    res0 = rank('./1.csv', {133:60,134:60,135:60,136:60},'score_total')
    print(res0)
    
    

    whole = rank_whole(csv_file='./1.csv', 
                       classes_counts={133:60,134:60,135:60,136:60}, 
                       score_names=['score_total','score_chinese','score_english','score_chemistry','score_physics',
                                    'score_mathematics','score_biology'])
    print(whole)
    whole.to_excel('./rank.xlsx')
