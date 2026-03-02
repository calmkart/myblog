---
title: "vim/nginx语法高亮插件"
date: 2017-11-20
description: "1.vim语法高亮插件molokai"
categories: 
  - "计算机"
tags: 
  - "nginx"
  - "vim"
  - "语法高亮"
---

1.vim语法高亮插件molokai

```bash
cd ~/.vim/
mkdir ./colors
cd ./colos
wget https://raw.githubusercontent.com/tomasr/molokai/master/colors/molokai.vim
echo colorscheme molokai  >> ~/.vimrc

```

<!--more-->

2.nginx语法高亮插件nginx.vim

```bash
mkdir -pv  ~/.vim/syntax
cd ~/.vim/syntax
wget -O nginx.vim  http://www.vim.org/scripts/download_script.php?src_id=19394
echo "au BufRead,BufNewFile /etc/nginx/*,/usr/local/nginx/conf/* if &ft == '' | setfiletype nginx | endif " >> ~/.vim/filetype.vim

```
