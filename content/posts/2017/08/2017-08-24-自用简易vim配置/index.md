---
title: "自用简易VIM配置"
date: 2017-08-24
categories: 
  - "计算机"
tags: 
  - "linux"
  - "vim"
---

最常用到的编辑器VIM，记录一下自用简易配置方式，方便需要的时候使用。

<!--more-->

 

```
cd
./.vimrc

```

./.vimrc

```
"去掉vi的一致性"
set nocompatible
" 隐藏滚动条"
set guioptions-=r
set guioptions-=L
set guioptions-=b
"隐藏顶部标签栏"
set showtabline=0
"设置字体"
set guifont=Monaco:h13
syntax on    "开启语法高亮"
set background=dark        "设置背景色"
set fileformat=unix    "设置以unix的格式保存文件"
set tabstop=4    "设置table长度"
set shiftwidth=4        "同上"
set showmatch    "显示匹配的括号"
set scrolloff=5        "距离顶部和底部5行"
set laststatus=2    "命令行为两行"
set fenc=utf-8      "文件编码"
set backspace=2
set mouse=n        "启用鼠标"
set selection=exclusive
set selectmode=mouse,key
set matchtime=5
set ignorecase        "忽略大小写"
set incsearch
set hlsearch        "高亮搜索项"
set expandtab        "不允许扩展table"
set autoread
set list
set listchars=tab:>-
set nu

map  :w:!python %

set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
Plugin 'VundleVim/Vundle.vim'
Plugin 'vim-airline/vim-airline'
call vundle#end()

let g:airline_powerline_fonts = 1

```

然后安装插件 这里主要安装Vundle管理插件以及界面美化插件vim-airline

1.安装Vundle

```
git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim

```

VIM下运行 :BundleInstall 进行安装插件 :BundleClean 卸载没有写在./.vimrc中的插件

2.安装vim-airline Plugin 'vim-airline/vim-airline' 既可

 

 

配置已上传github: [https://github.com/calmkart/vim\_config](https://github.com/calmkart/vim_config)
