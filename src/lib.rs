use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use std::collections::HashMap;
use std::fs::File;
use std::io::{self, BufRead, BufReader};

#[pymodule]
fn rust_parser(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_save_file, m)?)?;
    Ok(())
}

// データ構造
#[derive(Debug, Clone)]
enum Value {
    String(String),
    Integer(i64),
    Float(f64),
    Boolean(bool),
    Object(HashMap<String, Value>),
    Array(Vec<Value>),
}

#[pyfunction]
fn parse_save_file(py: Python, file_path: &str) -> PyResult<PyObject> {
    // 基本的なキーと値のペアのみ解析する単純な実装
    let file = match File::open(file_path) {
        Ok(file) => file,
        Err(e) => {
            return Err(PyErr::new::<pyo3::exceptions::PyIOError, _>(
                format!("Failed to open file: {}", e)
            ));
        }
    };
    let reader = BufReader::new(file);
    let mut result = HashMap::new();
    
    // ファイルを1行ずつ処理
    for line in reader.lines() {
        match line {
            Ok(line) => {
                // コメント行をスキップ
                if line.trim().starts_with('#') {
                    continue;
                }
                
                // キーと値のペアを検出
                if let Some(idx) = line.find('=') {
                    let key = line[..idx].trim().to_string();
                    let value_str = line[idx+1..].trim().to_string();
                    
                    // 値がオブジェクトや配列の場合はスキップ（ここでは単純化のため）
                    if value_str.starts_with('{') || value_str.contains('{') {
                        continue;
                    }
                    
                    // シンプルな値のみ処理
                    if let Ok(value) = parse_simple_value(&value_str) {
                        result.insert(key, value);
                    }
                }
            },
            Err(e) => {
                eprintln!("Warning: Failed to read line: {}", e);
            }
        }
    }
    
    // 解析結果をPythonオブジェクトに変換
    let dict = PyDict::new(py);
    for (key, value) in result {
        dict.set_item(key, value_to_py_object(py, &value)?)?;
    }
    
    // SaveDataクラスのインスタンスを作成
    let locals = PyDict::new(py);
    locals.set_item("data", dict)?;
    
    // SaveDataクラスをインポート
    let save_data_cls = py.import("paradox_savedata.parser.parser")?.getattr("SaveData")?;
    let save_data = save_data_cls.call((), Some(locals))?;
    
    Ok(save_data.into())
}

// シンプルな値（文字列、数値、ブール値）のみを解析
fn parse_simple_value(input: &str) -> Result<Value, String> {
    let trimmed = input.trim();
    
    // 空文字はエラー
    if trimmed.is_empty() {
        return Err("Empty value".to_string());
    }
    
    // 引用符付き文字列
    if trimmed.starts_with('"') && trimmed.ends_with('"') && trimmed.len() >= 2 {
        return Ok(Value::String(trimmed[1..trimmed.len()-1].to_string()));
    }
    
    // ブール値
    if trimmed.eq_ignore_ascii_case("yes") {
        return Ok(Value::Boolean(true));
    }
    if trimmed.eq_ignore_ascii_case("no") {
        return Ok(Value::Boolean(false));
    }
    
    // 数値
    if let Ok(num) = trimmed.parse::<i64>() {
        return Ok(Value::Integer(num));
    }
    
    // 浮動小数点数
    if let Ok(num) = trimmed.parse::<f64>() {
        return Ok(Value::Float(num));
    }
    
    // それ以外は文字列として扱う
    Ok(Value::String(trimmed.to_string()))
}

// Rust値をPythonオブジェクトに変換
fn value_to_py_object(py: Python, value: &Value) -> PyResult<PyObject> {
    match value {
        Value::String(s) => Ok(s.to_object(py)),
        Value::Integer(i) => Ok(i.to_object(py)),
        Value::Float(f) => Ok(f.to_object(py)),
        Value::Boolean(b) => Ok(b.to_object(py)),
        Value::Object(map) => {
            let dict = PyDict::new(py);
            for (key, val) in map {
                dict.set_item(key, value_to_py_object(py, val)?)?;
            }
            Ok(dict.to_object(py))
        },
        Value::Array(items) => {
            let list = PyList::empty(py);
            for item in items {
                list.append(value_to_py_object(py, item)?)?;
            }
            Ok(list.to_object(py))
        }
    }
}