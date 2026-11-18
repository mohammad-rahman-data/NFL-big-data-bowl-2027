import pandas as pd, numpy as np
from scipy.stats import spearmanr
DRILL="BACK_PEDAL_AND_90_DEGREE_BREAK_TO_BALL"
ct=pd.read_csv('combine_tracking.csv')
s=ct[(ct.drill_name==DRILL)&(ct.entity_type=='PLAYER')].copy()
s['t']=pd.to_datetime(s.time); s=s.sort_values(['nfl_id','attempt','t'])
rows=[]
for (pid,att),p in s.groupby(['nfl_id','attempt']):
    p=p.reset_index(drop=True); n=len(p)
    if n<20: continue
    idx=np.arange(n)
    dt=p.t.diff().dt.total_seconds().fillna(0.1).values.copy(); dt[dt<=0]=0.1
    v=np.r_[0,np.hypot(np.diff(p.x),np.diff(p.y))]/dt
    v=pd.Series(v).rolling(3,center=True,min_periods=1).mean().values
    acc=pd.Series(np.gradient(v)/0.1).rolling(3,center=True,min_periods=1).mean().values
    d=np.diff(p.dir.values); d=(d+180)%360-180; dd=np.r_[0,np.abs(d)]
    ok=np.where((v>=3)&(idx>=5)&(idx<n-5))[0]
    if len(ok)==0: continue
    b=ok[np.argmax(dd[ok])]
    rows.append(dict(nfl_id=pid,attempt=att,duration=(n-1)/10,
        pre_speed=v[max(b-10,0):b+1].max(),
        speed_after_1s=v[min(b+10,n-1)],
        cut_angle_deg=np.abs(d[max(b-3,0):b+3]).sum(),
        max_brake=-acc[max(b-5,0):b+6].min()))
f=pd.DataFrame(rows).sort_values('duration').drop_duplicates('nfl_id',keep='first')
f['speed_retained']=f.speed_after_1s/f.pre_speed
print('DB break features:',len(f))
print(f[['pre_speed','cut_angle_deg','max_brake','speed_retained']].describe().round(2).to_string())

# outcome: completion rate allowed on covered pass attempts, rookie regular season
pl=pd.read_csv('players.csv')
dbs=pl[pl.nfl_position.isin(['CB','SS','FS','DB'])][['nfl_id','draft_year']]
pp=pd.read_csv('player_play.csv',usecols=['game_id','nfl_id','coverage_assignment','pass_result'])
gm=pd.read_csv('games.csv',usecols=['game_id','season','season_type'])
pp=pp[pp.nfl_id.isin(dbs.nfl_id)&pp.pass_result.isin(['C','I','IN'])&(pp.coverage_assignment!='NO_ASSIGNMENT')]
pp=pp.merge(gm,on='game_id').merge(dbs,on='nfl_id')
pp=pp[(pp.season==pp.draft_year)&(pp.season_type=='REG')]
o=pp.groupby('nfl_id').agg(n=('pass_result','size'),comp=('pass_result',lambda x:(x=='C').mean())).reset_index()
for minn in [20,40]:
    d=f.merge(o[o.n>=minn],on='nfl_id')
    out=[f'min_plays={minn}',f'prospects={len(d)}']
    for c in ['cut_angle_deg','max_brake','speed_retained','pre_speed']:
        r,p=spearmanr(d[c],d.comp); out.append(f'{c}: rho={r:.2f} (p={p:.2f})')
    print(' | '.join(out))
f.to_csv('/home/claude/db_break_features.csv',index=False)
o.to_csv('/home/claude/db_outcomes.csv',index=False)
