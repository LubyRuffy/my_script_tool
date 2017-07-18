<?php
/**
 * Atuhor: Wizos
 * PubDate: 2016-11-30
 * Version: 1.0
 * description: 这是一个多看阅读的自动签到脚本，具体的说明见文章：
 */

$r_header['Cookie'] = '这里是你的 Cookie';
$r_header['Accept-Encoding'] = 'gzip,deflate';
$r_header['User-Agent'] = 'Dalvik/2.1.0 (Linux; U; Android 5.1; MX5 Build/LMY47I)';

// _t=1478918449&_c=10614 （一组实际的数据，作为参考）
function get_csrf_params ()
{
    $device_id = '这里是你的 Device_id';
    $time_sec = time();
    $array_of_str = get_array( $device_id.'&'.$time_sec );
    $i = 0;
    $csrf_code = 0;
    $size = count( $array_of_str );
    while ( $i < $size )
    {
        $csrf_code = generate( $csrf_code, $array_of_str[$i] );
        $i++;
    }
    $param = "_t=".$time_sec."&_c=".$csrf_code;
    echo '参数为：'.$param.'<br>';
    return $param;
}

function generate ( $paramInt, $paramString )
{
    $by = get_bytes( $paramString );
    return ($paramInt * 131 + $by[0]) % 65536;
}
function get_bytes($string) {  
        $bytes = array();  
        for($i = 0; $i < strlen($string); $i++){  
             $bytes[] = ord($string[$i]);  
        }  
        return $bytes;
}
function get_array ( $str )
{
    $arr = array();
    for($i=0;$i<strlen($str);$i++){
        $arr[$i] = $str[$i];
    }
return $arr;
}

function post( $url, $params ) {
    $curl = curl_init();//初始化curl模块
    curl_setopt($curl, CURLOPT_URL, $url );//登录提交的地址
    curl_setopt($curl, CURLOPT_HEADER, 0);//如果你想把一个头包含在输出中，设置这个选项为一个非零值
    curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);//设置不输出在浏览器上
    curl_setopt($curl, CURLOPT_COOKIE, $GLOBALS['r_header']["Cookie"] ); //设置Cookie信息保存在指定的文件中
    curl_setopt($curl, CURLOPT_HTTPHEADER, $GLOBALS['r_header'] );
    curl_setopt($curl, CURLOPT_POST, 1);//post方式提交
    curl_setopt($curl, CURLOPT_POSTFIELDS, $params );//要提交的信息
    if (preg_match('/^https/',$url)){
        //curl_setopt($curl, CURLOPT_SSL_VERIFYHOST, 1 );
        curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, 0 );
    }
    $data = curl_exec($curl);//执行cURL
    $curl_errno = curl_errno($curl);
    curl_close($curl);//关闭cURL资源，并且释放系统资源
    if($curl_errno>0){
        return 'error';
    }else{
        return $data;
    }
}

header('Content-Type: text/html; charset=utf-8') ;
$post_params = get_csrf_params();

$sign_in_msg = post( 'https://www.duokan.com/checkin/v0/checkin' , $post_params );
echo '<hr>';

$response = json_decode($sign_in_msg);
if ( $response->{'result'} == 0 )
{
    echo "签到成功：".$sign_in_msg;
}
else
{
    echo "签到失败：".$sign_in_msg;
}
    
?>