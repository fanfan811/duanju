from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# 使用 Windows 路径格式
FILE_PATH = os.path.join(os.path.dirname(__file__), "热门短剧.xlsx")

def load_dramas():
    """
    加载并返回短剧数据
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(FILE_PATH):
            print(f"文件不存在: {FILE_PATH}")
            return {"error": "文件不存在，请确保 '热门短剧.xlsx' 文件位于正确路径"}, 404
            
        # 读取Excel文件
        xls = pd.ExcelFile(FILE_PATH)
        df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
        
        # 检查数据是否为空
        if df.empty:
            print("Excel 文件为空")
            return {"error": "Excel 文件为空，请确保文件中有数据"}, 404
            
        # 检查列名是否存在
        required_columns = [df.columns[0], df.columns[1]]  # 使用实际列名
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"缺少必要的列名: {missing_columns}")
            return {
                "error": "Excel 文件中缺少必要的列名",
                "missing_columns": missing_columns,
                "available_columns": list(df.columns)  # 返回实际存在的列名
            }, 400
            
        # 只提取剧名和链接字段
        return df[[df.columns[0], df.columns[1]]].rename(columns={
            df.columns[0]: "name",
            df.columns[1]: "viewlink"
        }).to_dict(orient="records")
        
    except Exception as e:
        print(f"读取文件错误: {str(e)}")
        return {"error": f"读取文件错误: {str(e)}"}, 500

@app.route('/api/v1/dramas', methods=['GET'])
def get_all_dramas():
    """
    获取所有短剧数据，支持搜索
    """
    try:
        result = load_dramas()
        
        # 调试：打印返回的数据类型和内容
        print(f"load_dramas() returned type: {type(result)}")
        print(f"load_dramas() returned content: {result}")
        
        # 如果返回的是错误信息
        if isinstance(result, tuple):
            return jsonify(result[0]), result[1]
        
        # 确保result是列表
        if not isinstance(result, list):
            return jsonify({
                "code": 500,
                "message": f"Unexpected data format from load_dramas(): {type(result)}"
            }), 500
        
        # 获取搜索关键词
        keyword = request.args.get('keyword')
        
        # 如果有搜索关键词，过滤数据
        if keyword:
            # 确保每个drama都有name字段，并且是字符串
            filtered_dramas = [drama for drama in result 
                             if isinstance(drama, dict) and 
                             'name' in drama and 
                             isinstance(drama['name'], (str, int, float)) and 
                             keyword.lower() in str(drama['name']).lower()]
            return jsonify({
                "code": 200,
                "message": "success",
                "data": filtered_dramas
            })
        
        return jsonify({
            "code": 200,
            "message": "success",
            "data": result
        })
        
    except Exception as e:
        # 捕获并记录所有异常
        print(f"Error in get_all_dramas: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"Internal server error: {str(e)}"
        }), 500

@app.route('/api/v1/dramas/<int:id>', methods=['GET'])
def get_drama_by_id(id):
    """
    根据ID获取单个短剧
    """
    result = load_dramas()
    if isinstance(result, tuple):  # 如果有错误
        return jsonify(result[0]), result[1]
    if id < 0 or id >= len(result):
        return jsonify({"error": "ID超出范围"}), 400
    return jsonify({
        "code": 200,
        "message": "success",
        "data": result[id]
    })

@app.route('/api/v1/dramas/search', methods=['GET'])
def search_dramas():
    """
    根据关键词搜索短剧
    """
    keyword = request.args.get('keyword')
    if not keyword:
        return jsonify({"error": "缺少搜索关键词"}), 400
        
    result = load_dramas()
    if isinstance(result, tuple):  # 如果有错误
        return jsonify(result[0]), result[1]
        
    results = [drama for drama in result if keyword.lower() in drama['name'].lower()]
    return jsonify({
        "code": 200,
        "message": "success",
        "data": results
    })

@app.route('/api/v1/dramas/count', methods=['GET'])
def get_drama_count():
    """
    获取短剧总数
    """
    result = load_dramas()
    if isinstance(result, tuple):  # 如果有错误
        return jsonify(result[0]), result[1]
    return jsonify({
        "code": 200,
        "message": "success",
        "data": len(result)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
