import pygame
import random
import sys

# 初始化Pygame
pygame.init()

# 屏幕设置
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("粉笔字+粉笔末效果 - 鼠标左键绘制，右键清屏")

# 颜色定义（黑板灰黑+粉笔白/浅黄）
BLACKBOARD = (20, 25, 30)
CHALK_WHITE = (240, 240, 230)
CHALK_YELLOW = (245, 240, 200)

# 粒子类（模拟粉笔末）
class ChalkDust:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # 随机大小（1-3像素）
        self.size = random.randint(1, 3)
        # 随机颜色（偏白/偏黄的粉笔色）
        self.color = random.choice([CHALK_WHITE, CHALK_YELLOW])
        # 随机下落速度（模拟重力）
        self.speed_y = random.uniform(1, 3)
        # 随机横向偏移（模拟轻微飘移）
        self.speed_x = random.uniform(-0.5, 0.5)
        # 生命周期（帧数）
        self.life = random.randint(30, 80)

    def update(self):
        # 更新位置（下落+飘移）
        self.y += self.speed_y
        self.x += self.speed_x
        # 生命周期减少
        self.life -= 1
        # 速度轻微增加（模拟重力加速度）
        self.speed_y += 0.05

    def draw(self):
        # 绘制粉笔末粒子
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

# 主程序变量
clock = pygame.time.Clock()
drawing = False  # 是否正在绘制
last_pos = None  # 上一帧鼠标位置
brush_size = 8   # 粉笔粗细
dust_list = []   # 粉笔末粒子列表

# 主循环
running = True
while running:
    # 控制帧率（60帧/秒）
    clock.tick(60)
    
    # 填充黑板背景
    screen.fill(BLACKBOARD)

    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # 鼠标左键按下：开始绘制
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键
                drawing = True
                last_pos = pygame.mouse.get_pos()
            elif event.button == 3:  # 右键清屏
                dust_list.clear()
                screen.fill(BLACKBOARD)
        # 鼠标左键松开：停止绘制
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                drawing = False
                last_pos = None

    # 绘制逻辑
    if drawing:
        current_pos = pygame.mouse.get_pos()
        if last_pos:
            # 1. 绘制粉笔线条（带纹理：随机偏移+噪点）
            # 基础线条
            pygame.draw.line(screen, CHALK_WHITE, last_pos, current_pos, brush_size)
            # 添加粉笔纹理（随机小点点）
            for _ in range(5):
                offset_x = random.randint(-brush_size//2, brush_size//2)
                offset_y = random.randint(-brush_size//2, brush_size//2)
                texture_x = current_pos[0] + offset_x
                texture_y = current_pos[1] + offset_y
                pygame.draw.circle(screen, CHALK_YELLOW, (texture_x, texture_y), 1)
            
            # 2. 生成粉笔末粒子（每帧生成5-10个）
            for _ in range(random.randint(5, 10)):
                dust = ChalkDust(current_pos[0], current_pos[1])
                dust_list.append(dust)
            
            # 更新上一帧位置
            last_pos = current_pos

    # 更新并绘制所有粉笔末粒子
    for dust in dust_list[:]:  # 遍历副本，避免删除时出错
        dust.update()
        dust.draw()
        # 粒子生命周期结束则移除
        if dust.life <= 0:
            dust_list.remove(dust)

    # 更新屏幕显示
    pygame.display.flip()

# 退出程序
pygame.quit()
sys.exit()