# Author: Chen Guoyi, guoyi@comp.nus.edu.sg, NUS Computing
import json


class JsonConfigMngr:
    def __init__(self, config_file='param/config.json'):
        self.config_file = config_file
        self.config = {'port':'COM6', 'gport':'COM17'}
        with open(self.config_file, 'w') as config_file:
            json.dump(self.config, config_file, indent=4)
            print("配置文件已创建并成功读取。")

    def load_config(self, *keys):
        '''
        加载并返回指定配置项，支持任意层级
        keys: 可变参数表示配置路径 (如 'SERIAL_PORT', 'ARM', 'USB_PORT')
        返回: 对应的配置值或整个配置字典
        '''
        try:
            with open(self.config_file, 'r') as file:
                self.config = json.load(file)  
            if not keys:  # 无参数时返回整个配置
                return self.config
            current = self.config
            for key in keys:
                current = current[key]
            return current
        except FileNotFoundError:
            print("未找到配置文件.")
            return None
        except KeyError as e:
            print(f"配置项不存在: {e}")
            return None

    def update_config(self, *keys, config_value):
        '''
        支持任意层级的配置项更新
        keys: 可变参数表示配置路径 (如 'SERIAL_PORT', 'ARM', 'USB_PORT')
        config_value: 要设置的配置值
        '''
        try:
            with open(self.config_file, 'r') as config_file:
                self.config = json.load(config_file)
            # 逐层遍历配置字典
            current_level = self.config
            for key in keys[:-1]:  # 除最后一级外的所有层级
                if key not in current_level:
                    current_level[key] = {}  # 创建不存在的中间层级
                current_level = current_level[key]
            # 设置最终层级的值
            current_level[keys[-1]] = config_value
            with open(self.config_file, 'w') as config_file:
                json.dump(self.config, config_file, indent=4)
                print("配置文件已更新。")
        except FileNotFoundError:
            print("未找到配置文件.")
        except IndexError:
            print("至少需要提供一个配置键")

    def delete_config(self, *keys):
        '''
        删除指定配置项（支持任意层级）
        keys: 可变参数表示配置路径 (如 'SERIAL_PORT', 'ARM')
        '''
        try:
            with open(self.config_file, 'r') as config_file:
                self.config = json.load(config_file)
            current_level = self.config
            # 遍历到父节点
            for key in keys[:-1]:
                current_level = current_level[key]
            # 删除目标节点
            del current_level[keys[-1]]
            with open(self.config_file, 'w') as config_file:
                json.dump(self.config, config_file, indent=4)
                print("配置项已删除。")
        except FileNotFoundError:
            print("未找到配置文件.")
        except KeyError as e:
            print(f"配置路径不存在: {'/'.join(keys)}")
        except IndexError:
            print("至少需要提供一个配置键")
