
这个脚本是用来进行steam 挂机游戏firestone的自动化处理。  

可以自动进行**公会远征**、**地图任务**、**守卫训练**、**科技树升级**、**转生爬楼**等功能。  

解放双手，超护肝脚本。  

# 1. 如何使用  

当前firestone 游戏版本:  4.1.1  
当前代码在Macbook Pro 13-inch下的笔记本上测试通过。  
当前代码的默认逻辑为: 
+ 科技树III
+ 守卫训练时训练小火龙

#### 运行代码

```python3
python main.py
```

# 2. 代码流程图

```flow
st=>start: 开始
exit=>operation: 回到挂机主界面
guard=>operation: 进行守卫训练
tree=>operation: 进行科技树升级
family=>operation: 进行工会远征任务
map_init=>operation: 进行地图任务初始化
map_check=>condition: 是否需要进行地图任务
map_run=>operation: 按地图任务优先级进行任务
guaji=>operation: 挂机(设置技能释放)
e=>end

st->exit->guard->tree->family->map_init->map_check
map_check(yes)->map_run
map_check(no)->guaji
map_run->guaji
```

# 3. 环境依赖  

+ python3.6
+ opencv

# 4. To Do Lists

- [ ] 跨平台测试运行
- [ ] 公会远征逻辑优化
- [ ] 科技树升级自动化判断
- [ ] 图形用户界面简化操作流程

# 5. FQA
1. 

# 6. Release Notes

# 7. Contribution
如何觉得这个游戏脚本使用起来有问题，可以开一个ISSUE来描述。

如何觉得代码逻辑可以优化，欢迎提PR来优化。

如何觉得这个项目对你有帮助，请点个star. 