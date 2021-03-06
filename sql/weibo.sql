create database weibo;

use weibo;

# uid必须设置为bigint，否则会超出范围
create table IF NOT EXISTS top100(
	date varchar(200) not null,
    period_type varchar(10) not null,
	field_id int not null,
    field_name varchar(30) not null,
	uid bigint not null, 
    screen_name varchar(120) not null,
    score float not null,
    curr_rank int not null,
    last_rank int null,
    rank_up_down varchar(10) null
)CHARSET=utf8mb4;

create table IF NOT EXISTS user_info(
	uid bigint not null, 
    screen_name varchar(120) not null,
    authentication_grade varchar(20),
    industry_category varchar(400),
    sex varchar(20),
    location varchar(50),
    sexual_orientation varchar(50),
    marriage varchar(50),
    birthday varchar(50),
    blood_type varchar(20),
    blog varchar(200),
    style_domain varchar(200),
    intro varchar(400),
    regist_time date,
    ip_region varchar(50),
    authentication varchar(400),
    company varchar(400),
    university varchar(400),
    tags varchar(400),
    follower_num int,
    fans_num int,
    post_num int,
    growth_value int,
    vip_rank int
)CHARSET=utf8mb4;

create table IF NOT EXISTS friend(
	friendship varchar(20) not null,
    uid bigint not null,
	id bigint not null,
    idstr varchar(50) not null,
    class int,
    name varchar(120) not null,
    province int,
    city int,
    location varchar(50),
    description varchar(400),
    url varchar(200),
    profile_image_url varchar(200),
    cover_image_phone varchar(1000),
    profile_url varchar(200),
    domain varchar(200),
    gender varchar(20),
    followers_count bigint,
    followers_count_str varchar(50),
    friends_count int,
    pagefriends_count int,
    statuses_count int,
    video_status_count int,
    video_play_count int,
    favourites_count int,
    created_at varchar(200),
    allow_all_act_msg boolean,
    geo_enabled boolean,
    verified boolean,
    verified_type int,
    status_id bigint,
    status_idstr varchar(50),
    ptype int,
    allow_all_comment boolean,
    verified_reason varchar(400),
    verified_trade varchar(200),
    verified_reason_url varchar(200),
    verified_source varchar(400),
    verified_source_url varchar(200),
    bi_followers_count int,
    lang varchar(20),
    star int,
    mbtype int,
    mbrank int,
    svip int,
    block_word int,
    block_app int,
    chaohua_ability int,
    brand_ability int,
    nft_ability int,
    credit_score int,
    user_ability int,
    urank int,
    story_read_state int,
    vclub_member  int,
    is_teenager int,
    is_guardian int,
    is_teenager_list int,
    pc_new int,
    special_follow boolean,
    planet_video int,
    video_mark int,
    live_status int,
    user_ability_extend int,
    brand_account int,
    hongbaofei int,
    sexual_content boolean,
    status_total_cnt int,
    status_repost_cnt int,
    status_comment_cnt int,
    status_like_cnt int,
    status_comment_like_cnt int
)CHARSET=utf8mb4;

create table IF NOT EXISTS weibo(
	mid varchar(50) not null,
	uid bigint not null, 
    screen_name varchar(120) not null,
    created_at datetime not null,
    app_source varchar(200),
    pictures varchar(2000),
    content varchar(3000),
    content_topics varchar(1500),
    urls varchar(2000),
    forward_count int,
    comment_count int,
    like_count int
)CHARSET=utf8mb4;

create table IF NOT EXISTS first_comment(
    mid varchar(50) not null,
    comment_id varchar(50) not null,
    created_at datetime not null,
    floor_number int not null,
    content varchar(3000),
    source varchar(200),
	comment_badge varchar(50),
    reply_count int,
    like_count int,
    uid bigint not null, 
    screen_name varchar(120) not null,
    home_url varchar(200),
    gender varchar(20),
    weibo_count int,
    verified boolean,
    verified_type int,
    verified_type_ext int,
    verified_reason varchar(400),
    description varchar(400),
    mbtype int,
    urank int,
    mbrank int,
    followers_count int,
    fans_count int
)CHARSET=utf8mb4;

create table IF NOT EXISTS second_comment(
    first_comment_id varchar(50) not null,
    comment_id varchar(50) not null,
    created_at datetime not null,
    floor_number int not null,
    content varchar(3000),
    source varchar(200),
	comment_badge varchar(50),
    reply_count int,
    like_count int,
    uid bigint not null, 
    screen_name varchar(120) not null,
    home_url varchar(200),
    gender varchar(20),
    weibo_count int,
    verified boolean,
    verified_type int,
    verified_type_ext int,
    verified_reason varchar(400),
    description varchar(400),
    mbtype int,
    urank int,
    mbrank int,
    followers_count int,
    fans_count int
)CHARSET=utf8mb4;

# 删除数据表
# drop table top100;
# drop table user_info;
# drop table friend;
# drop table weibo;
# drop table first_comment;
# drop table second_comment;