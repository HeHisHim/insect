CREATE DATABASE `insect` DEFAULT CHARACTER SET utf8;

use insect;

CREATE TABLE urls (
    id bigint unsigned NOT NULL AUTO_INCREMENT COMMENT '队列索引',
    url varchar(512) NOT NULL COMMENT '链接',
    md5Code char(16) NOT NULL COMMENT '链接编码的md5',
    status varchar(11) NOT NULL DEFAULT "new" COMMENT '可以为new, downloading 和 finish',
    depth varchar(11) NOT NULL COMMENT '爬取深度',
    queue_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    done_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    PRIMARY KEY (id),
    UNIQUE (md5Code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='爬虫信息';