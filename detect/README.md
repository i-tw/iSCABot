# iSCABot/detect

漏洞检测代码

本漏洞检测代码支持 c/cpp 源代码以及未加壳二进制可执行 elf 文件的漏洞检测。

本代码使用 clang, retdec 等工具将源代码与二进制文件转换为 llvm 中间代码，之后使用 llvm2cpg 工具，从 llvm 中间代码中提取代码属性图信息，之后使用 joern 工具对代码属性图信息进行整理与筛选，生成 pandas.DataFrame 格式的数据文件。之后经过 w2v 的特征处理，通过神经网络进行漏洞的识别与检测。

## 使用方法

```bash
python3 analyse_all.py \
	--input-path "${input_path}" \
	--llvm-path "${llvm_path}" \
	--cpg-path "${cpg_path}" \
	--output-path "${output_path}" \
	--log "${log_path}"

```

使用上述命令行，可以对目标文件目录下的代码进行漏洞检测，并将检测结果存储在本地的 mysql 数据库中

- `${input_path}` 待检测的项目文件目录

- `${llvm_path}` 中间产生的 llvm 中间代码目标目录

- `${cpg_path}` 中间产生的 cpg 文件目标目录

- `${output_path}` 中间产生的 pandas.DataFrame 数据文件的目标目录

- `${log_path}` 从源项目文件到 w2v 处理之前的目标日志文件



## 项目文件要求

目标项目文件夹根目录必须包含一个项目配置文件 `conf.xml`，其格式如下：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configure>
<basic>
    <name>try_code</name>
    <version>0.0.1</version>
</basic>

<project>
    <source>
        <dir>src</dir>
    </source>

    <include>
        <dir>inc</dir>
    </include>

    <binary>
        <dir>bin</dir>
    </binary>
</project>

</configure>
```

- `configure.basic.name` 字段说明项目名称

- `configure.basic.version` 字段说明项目版本号

- `configure.project.source` 字段说明待检测的 c/cpp 源文件目录

- `configure.project.include` 字段说明待检测的 c/cpp 源文件编译需要链接的头文件的目录

- `configure.project.binary` 字段说明待检测的二进制可执行文件目录

注：project 字段的三个子字段都可以拥有多个 dir 子字段

## 参考

- [clang/llvm](https://llvm.org/)

- [retdec](https://github.com/avast/retdec)

- [llvm2cpg](https://github.com/ShiftLeftSecurity/llvm2cpg)

- [joern](joern.io)

