CREATE EXTENSION "uuid-ossp";

CREATE EXTENSION "pg_trgm";

-- 用户
CREATE TABLE "t_user"(
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "nickname" VARCHAR(32) NOT NULL DEFAULT '',
    -- 昵称
    "phone" VARCHAR(32) NOT NULL DEFAULT '',
    -- 手机号
    "avatar" VARCHAR(1024) NOT NULL DEFAULT '',
    -- 用户头像
    "gender" VARCHAR(32) NOT NULL DEFAULT '',
    --性别
    "status" VARCHAR(32) NOT NULL DEFAULT 'OK',
    -- 状态
    "wxopenid" VARCHAR(256) NOT NULL DEFAULT '',
    -- 绑定的微信Open ID
    "wxunionid" VARCHAR(128) NOT NULL DEFAULT '',
    -- 绑定微信的Union ID
    "salt" VARCHAR(64) NOT NULL DEFAULT '',
    "password" VARCHAR(256) NOT NULL DEFAULT '',
    "ptype" VARCHAR(32) NOT NULL DEFAULT '',
    "created_time" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON "t_user"("phone");

CREATE INDEX ON "t_user"("wxopenid");

CREATE INDEX ON "t_user"("status");

CREATE INDEX ON "t_user"("wxunionid");


-- 用户登录记录
CREATE TABLE "t_user_token"(
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "user_id" BIGINT NOT NULL, -- 用户ID
    "device" VARCHAR(1024) NOT NULL, -- 登陆设备，网页登陆则为User-Agent
    "method" VARCHAR(32) NOT NULL DEFAULT '',
    -- 登录方式
    "ip" VARCHAR(256) NOT NULL,
    "expired_time" TIMESTAMP WITH TIME ZONE,
    "status" VARCHAR(32) NOT NULL DEFAULT 'OK',
    "created_time" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON "t_user_token"("user_id", "status");

CREATE INDEX ON "t_user_token"("user_id", "expired_time");

CREATE INDEX ON "t_user_token"("method");

CREATE INDEX ON "t_user_token"("created_time");

/* 内部管理人员 */
CREATE TABLE "t_admin_staff" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(32) NOT NULL, -- 登陆用户名
    "name" VARCHAR(32) NOT NULL, -- 姓名，用于展示
    "salt" VARCHAR(32) NOT NULL,
    "ptype" VARCHAR(16) NOT NULL,
    "password" VARCHAR(256) NOT NULL,
    "status" VARCHAR(32) NOT NULL DEFAULT 'OK',
    "phone" VARCHAR(32) NOT NULL DEFAULT '',
    "email" VARCHAR(128) NOT NULL DEFAULT '',
    "is_superuser" BOOLEAN NOT NULL DEFAULT FALSE,
    "created_by" BIGINT,
    "created_time" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE ("username")
);

CREATE INDEX ON "t_admin_staff" USING GIN ("username" gin_trgm_ops);

CREATE INDEX ON "t_admin_staff" USING GIN ("name" gin_trgm_ops);

CREATE INDEX ON "t_admin_staff" USING GIN ("phone" gin_trgm_ops);

CREATE INDEX ON "t_admin_staff" USING GIN ("email" gin_trgm_ops);

CREATE INDEX ON "t_admin_staff" ("status");

-- 管理员账号的登陆记录
CREATE TABLE "t_admin_staff_token" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    "staff_id" BIGINT NOT NULL,
    "device" VARCHAR(1024) NOT NULL,
    "ip" VARCHAR(256) NOT NULL,
    "expired_time" TIMESTAMP WITH TIME ZONE,
    "status" VARCHAR(32) NOT NULL DEFAULT 'OK',
    "created_time" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON "t_admin_staff_token" ("staff_id", "status");

CREATE INDEX ON "t_admin_staff_token" ("staff_id", "expired_time");

CREATE INDEX ON "t_admin_staff_token" ("created_time");