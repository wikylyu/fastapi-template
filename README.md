# fastapi-template
FastAPI框架的模板，可以与[angular-dashboard-template](https://github.com/wikylyu/angular-dashboard-template)配合


## Consul 配置

此项目使用[consul](https://www.consul.io/)的KV功能作为配置服务，具体配置如下：

* template/http
```json
{
  "session": "aze4e6a5ab7903d9ab587e7b0xaac184750250",
  "cors":{
    "AllowOrigins": [
      "http://127.0.0.1:4200"
    ],
    "AllowCredentials":true
  }
}
```
* template/db
```json
{
  "psql": {
  	"dsn": "postgresql://postgres@127.0.0.1/template?sslmode=disable"
  }
}
```

## 数据库
此项目使用PostgreSQL作为关系数据库。具体数据表定义在[doc/schema.sql](https://github.com/wikylyu/fastapi-template/blob/main/doc/schema.sql)。

根据需要修改数据表的前缀，默认为**t_**，同时需要修改文件[db/psql.py](https://github.com/wikylyu/fastapi-template/blob/7ef525cfaa14641a8ea35a58ea3eb5652b0a4091/db/psql.py#L19)中**TableBase**的**_table_prefix**属性。

可以用以下方式创建数据库：
```sql
CREATE DATABASE template WITH ENCODING=UTF-8;
\c tempalte;
\i doc/schema.sql;
```