import pygame
import random
import sys
import imageio # 用于生成gif

# 初始化Pygame
pygame.init()

# 屏幕设置
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("粉笔字+粉笔末效果 - 左键绘制，右键清屏")

# 离屏表面保存笔迹（设置为和屏幕同尺寸，透明背景）
drawing_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
drawing_surface.fill((0, 0, 0, 0))

# 颜色定义
BLACKBOARD = (20, 25, 30)       # 黑板底色
CHALK_WHITE = (240, 240, 230)   # 粉笔白
CHALK_YELLOW = (245, 240, 200)  # 粉笔黄

# 粒子类（粉笔末）
class ChalkDust:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(1, 2)  # 粉笔末大小
        self.color = random.choice([CHALK_WHITE, CHALK_YELLOW])
        self.speed_y = random.uniform(0.8, 2)  # 下落速度
        self.speed_x = random.uniform(-0.3, 0.3)  # 横向飘移
        self.life = random.randint(20, 70)  # 生命周期

    def update(self):
        self.y += self.speed_y
        self.x += self.speed_x
        self.speed_y += 0.03  # 轻微重力加速
        self.life -= 1

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

# 主程序变量
clock = pygame.time.Clock()
drawing = False
last_pos = None  # 记录上一帧鼠标位置，保证线条连续
brush_size = 4   # 粉笔粗细（3像素，细腻）
dust_count = 2   # 每帧生成的粉笔末数量
dust_list = []   # 粉笔末列表（移到循环外，避免重复定义）

# 新增：录屏相关变量
recording = False  # 是否正在录制
frame_list = []    # 存储录制的帧

# 主循环
running = True
while running:
    clock.tick(120)  # 120帧高帧率，解决笔迹间隙
    screen.fill(BLACKBOARD)  # 填充黑板背景

    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # 鼠标左键按下：开始绘制
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                drawing = True
                last_pos = pygame.mouse.get_pos()  # 记录初始位置
            # 右键清屏
            elif event.button == 3:
                drawing_surface.fill((0, 0, 0, 0))  # 清空笔迹
                dust_list.clear()  # 清空粉笔末
        # 鼠标左键松开：停止绘制
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                drawing = False
                last_pos = None
               # 新增：F1开始录制，F2停止并保存GIF
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not recording:
                recording = True
                frame_list.clear()
                print("开始录制！按F2保存GIF到桌面")
            elif event.key == pygame.K_SPACE and recording:
                recording = False
                # 保存GIF到桌面，帧率15，循环播放（0=无限循环）
                gif_path = "C:/Users/Administrator/Desktop/粉笔字效果.gif"
                # 替换上面的 你的用户名 为实际电脑用户名，比如 C:/Users/zhangsan/Desktop/
                imageio.mimsave(gif_path, frame_list, duration=1/15, loop=0)
                print(f"GIF已保存到：{gif_path}")

    # 绘制逻辑（核心：连续细线条，无间隙）
    if drawing:
        current_pos = pygame.mouse.get_pos()
        if last_pos and current_pos != last_pos:
            # 1. 绘制连续细线条（移除错误的抗锯齿参数，解决报错）
            pygame.draw.line(
                drawing_surface, 
                CHALK_WHITE, 
                last_pos, 
                current_pos, 
                brush_size  # 仅保留粗细参数，去掉SRCALPHA
            )
            # 2. 补充粉笔纹理点（模拟真实粉笔质感）
            for _ in range(2):
                offset_x = random.randint(-brush_size//2+1, brush_size//2+1)
                offset_y = random.randint(-brush_size//2+1, brush_size//2+1)
                texture_x = current_pos[0] + offset_x
                texture_y = current_pos[1] + offset_y
                texture_color = random.choice([CHALK_WHITE, CHALK_YELLOW])
                pygame.draw.circle(drawing_surface, texture_color, (texture_x, texture_y), 1)
            
            # 3. 生成粉笔末
            for _ in range(dust_count):
                dust = ChalkDust(current_pos[0], current_pos[1])
                dust_list.append(dust)
            
            # 更新上一位置，保证线条连续
            last_pos = current_pos

    # 更新并绘制所有粉笔末
    for dust in dust_list[:]:
        dust.update()
        dust.draw()
        if dust.life <= 0:
            dust_list.remove(dust)

    # 将笔迹绘制到主屏幕（核心：保留永久笔迹）
    screen.blit(drawing_surface, (0, 0))

    # 更新屏幕显示
    pygame.display.flip()

    # 新增：如果正在录制，捕获当前帧并添加到列表
    if recording:
        # 将pygame屏幕转换为imageio支持的格式
        frame = pygame.surfarray.array3d(screen)
        frame = frame.transpose(1, 0, 2)  # 调整坐标顺序
        frame_list.append(frame)

# 退出程序
pygame.quit()
sys.exit()
