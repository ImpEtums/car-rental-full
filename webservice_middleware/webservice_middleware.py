import json
import xml.etree.ElementTree as ET
from functools import wraps
from flask import request, Response

def webservice_support(f):
    """
    WebService支持装饰器
    根据请求头自动处理JSON和XML格式的请求和响应
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查请求的Content-Type
        content_type = request.headers.get('Content-Type', '')
        accept_header = request.headers.get('Accept', '')
        
        # 处理XML请求
        if 'application/xml' in content_type or 'text/xml' in content_type:
            try:
                # 解析XML请求数据
                xml_data = request.data.decode('utf-8')
                parsed_data = parse_xml_to_dict(xml_data)
                
                # 将解析后的数据注入到request对象中
                request.xml_data = parsed_data
                
            except Exception as e:
                return create_xml_error_response(f"XML解析错误: {str(e)}", 400)
        
        # 执行原始函数
        try:
            result = f(*args, **kwargs)
            
            # 检查是否需要返回XML格式
            if ('application/xml' in accept_header or 
                'text/xml' in accept_header or 
                'application/xml' in content_type or 
                'text/xml' in content_type):
                
                # 如果result是Flask Response对象，提取数据
                if hasattr(result, 'get_json'):
                    try:
                        data = result.get_json()
                        status_code = result.status_code
                    except:
                        data = {'message': 'Response conversion error'}
                        status_code = 500
                elif isinstance(result, tuple):
                    # 处理 (data, status_code) 格式的返回值
                    if len(result) >= 2:
                        data = result[0].get_json() if hasattr(result[0], 'get_json') else result[0]
                        status_code = result[1]
                    else:
                        data = result[0]
                        status_code = 200
                else:
                    data = result
                    status_code = 200
                
                # 转换为XML格式返回
                xml_response = convert_to_xml(data)
                return Response(xml_response, 
                              status=status_code, 
                              mimetype='application/xml',
                              headers={'Content-Type': 'application/xml; charset=utf-8'})
            
            # 默认返回原始结果
            return result
            
        except Exception as e:
            # 错误处理
            if ('application/xml' in accept_header or 
                'text/xml' in accept_header or 
                'application/xml' in content_type or 
                'text/xml' in content_type):
                return create_xml_error_response(f"服务器错误: {str(e)}", 500)
            else:
                raise e
    
    return decorated_function

def parse_xml_to_dict(xml_string):
    """
    将XML字符串解析为Python字典
    """
    try:
        root = ET.fromstring(xml_string)
        return xml_element_to_dict(root)
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML format: {str(e)}")

def xml_element_to_dict(element):
    """
    递归将XML元素转换为字典
    """
    result = {}
    
    # 处理元素属性
    if element.attrib:
        result['@attributes'] = element.attrib
    
    # 处理子元素
    children = list(element)
    if children:
        child_dict = {}
        for child in children:
            child_data = xml_element_to_dict(child)
            if child.tag in child_dict:
                # 如果标签已存在，转换为列表
                if not isinstance(child_dict[child.tag], list):
                    child_dict[child.tag] = [child_dict[child.tag]]
                child_dict[child.tag].append(child_data)
            else:
                child_dict[child.tag] = child_data
        result.update(child_dict)
    
    # 处理文本内容
    if element.text and element.text.strip():
        if result:  # 如果已有子元素或属性
            result['#text'] = element.text.strip()
        else:  # 如果只有文本内容
            return element.text.strip()
    
    return result if result else None

def convert_to_xml(data, root_name='response'):
    """
    将Python数据结构转换为XML字符串
    """
    def dict_to_xml(d, parent_element):
        if isinstance(d, dict):
            for key, value in d.items():
                if key.startswith('@'):  # 跳过属性标记
                    continue
                elif key == '#text':  # 处理文本内容
                    parent_element.text = str(value)
                else:
                    child_element = ET.SubElement(parent_element, str(key))
                    dict_to_xml(value, child_element)
        elif isinstance(d, list):
            for item in d:
                item_element = ET.SubElement(parent_element, 'item')
                dict_to_xml(item, item_element)
        else:
            parent_element.text = str(d) if d is not None else ''
    
    # 创建根元素
    root = ET.Element(root_name)
    
    # 添加XML声明属性
    root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    
    # 转换数据
    dict_to_xml(data, root)
    
    # 生成XML字符串
    xml_str = ET.tostring(root, encoding='unicode', method='xml')
    
    # 添加XML声明
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'

def create_xml_error_response(message, status_code):
    """
    创建XML格式的错误响应
    """
    error_data = {
        'error': {
            'message': message,
            'code': status_code
        }
    }
    xml_response = convert_to_xml(error_data, 'error_response')
    return Response(xml_response, 
                   status=status_code, 
                   mimetype='application/xml',
                   headers={'Content-Type': 'application/xml; charset=utf-8'})

def create_soap_envelope(body_content, action=None):
    """
    创建SOAP信封格式的XML响应
    """
    soap_template = '''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <soap:Body>
        {body}
    </soap:Body>
</soap:Envelope>'''
    
    return soap_template.format(body=body_content)

def soap_webservice_support(action_name):
    """
    SOAP WebService支持装饰器
    专门处理SOAP格式的请求和响应
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            content_type = request.headers.get('Content-Type', '')
            
            # 检查是否为SOAP请求
            if 'text/xml' in content_type or 'application/soap+xml' in content_type:
                try:
                    # 解析SOAP请求
                    xml_data = request.data.decode('utf-8')
                    root = ET.fromstring(xml_data)
                    
                    # 提取SOAP Body内容
                    namespaces = {
                        'soap': 'http://schemas.xmlsoap.org/soap/envelope/'
                    }
                    body = root.find('.//soap:Body', namespaces)
                    
                    if body is not None:
                        # 将Body内容转换为字典
                        body_data = {}
                        for child in body:
                            body_data.update(xml_element_to_dict(child))
                        request.soap_data = body_data
                    
                except Exception as e:
                    error_response = create_soap_fault(f"SOAP解析错误: {str(e)}")
                    return Response(error_response, 
                                  status=400, 
                                  mimetype='text/xml')
            
            # 执行原始函数
            try:
                result = f(*args, **kwargs)
                
                # 如果是SOAP请求，返回SOAP格式响应
                if 'text/xml' in content_type or 'application/soap+xml' in content_type:
                    if hasattr(result, 'get_json'):
                        data = result.get_json()
                    elif isinstance(result, tuple):
                        data = result[0].get_json() if hasattr(result[0], 'get_json') else result[0]
                    else:
                        data = result
                    
                    # 创建SOAP响应
                    response_xml = convert_to_xml(data, f'{action_name}Response')
                    soap_response = create_soap_envelope(response_xml)
                    
                    return Response(soap_response, 
                                  status=200, 
                                  mimetype='text/xml',
                                  headers={
                                      'Content-Type': 'text/xml; charset=utf-8',
                                      'SOAPAction': f'"{action_name}"'
                                  })
                
                return result
                
            except Exception as e:
                if 'text/xml' in content_type or 'application/soap+xml' in content_type:
                    fault_response = create_soap_fault(f"服务器错误: {str(e)}")
                    return Response(fault_response, 
                                  status=500, 
                                  mimetype='text/xml')
                else:
                    raise e
        
        return decorated_function
    return decorator

def create_soap_fault(message):
    """
    创建SOAP Fault响应
    """
    fault_template = '''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <soap:Fault>
            <faultcode>Server</faultcode>
            <faultstring>{message}</faultstring>
        </soap:Fault>
    </soap:Body>
</soap:Envelope>'''
    
    return fault_template.format(message=message)