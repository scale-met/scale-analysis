
# 富岳でのPython使用手順
このドキュメントでは富岳でPythonおよびXarray等のPython用ライブラリを用いる手順を説明します。
(2024.11.7時点)

## ログインノードの場合
### 前置き
富岳ではシステム管理者が初めから利用可能にしているPython環境がありますが、ライブラリが一部不足しています。
そのためここではpyenv等を用いて自前で環境構築する手順について説明します。
* システムのデフォルトのPython環境はversion2.7もしくは3.6
* システム管理者がSpackを用いて提供しているPython環境はversion3.10
* Pythonライブラリの一部はpy-から始まるパッケージ名でSpackを使ってインストールされています。（ログインノード向けはlinux-rhel8-cascadelakeまたは linux-rhel8-skylake_avx512）

### 自前のPython環境を構築する
* 自分のアカウントのデータ領域に非管理者の権限でPython 環境を構築するために[pyenv](https://github.com/pyenv/pyenv) を導入します。
* [このページ](https://github.com/pyenv/pyenv)を参考にpyenvの初期設定を行った後、pyenvを用いてPython環境をインストールします。例えば以下の様にpyenvを用いて最新のminiconda3をインストールできます。
  ```
  $ pyenv install miniconda3-latest
  ```
* さらに、必要なPythonライブラリ(xarray, matplotlib, numpy, …等) をpip コマンドで追加します。
  ```
  $ pip install ライブラリ名
  ```

## 計算ノードの場合

* ここではシステム管理者がSpackを用いて提供しているPython環境を用います。

* 計算ノードでPython環境を使用するためには、Spackジョブスクリプトの冒頭で、必要なライブラリを以下の様にロードする必要します。

```
. /vol0004/apps/oss/spack/share/spack/setup-env.sh

spack load --first py-netcdf4%fj
spack load --first py-dask%fj
spack load --first py-xarray%fj
spack load --first py-matplotlib%fj  
spack load --first py-joblib%fj　　　
```
ここではnetcdf、dask、xarray、matplotlib (作図でmatplotlibを用いる場合)、joblib(並列化にjoblibを用いる場合)のライブラリをロードしています。

* llio_transferは以下の様なコマンドで指定します。
```
export LD_PRELOAD=/usr/lib/FJSVtcs/ple/lib64/libpmix.so
 ``` 
* mpiexecを以下の様に指定します。

```
 mpiexec -n 1 python3 ./実行したいPythonのファイル名.py
 ```


### 補足事項　(2023.8.1時点)
* 計算ノードではXarrayがインストール済みです。
* 計算ノードでpy-netcdf4 を使う際には、環境変数(LD_PRELOAD)の設定とmpiexecを使ってpythonスクリプトを実行する必要があります。
