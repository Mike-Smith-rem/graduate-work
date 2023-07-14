<template>
  <div class="hello">
    <el-container>
      <el-header>面向PDF文档的信息抽取与关键信息检索</el-header>
      <el-main>
        <el-card>
          <el-row class="para-1">
            <el-col :span="8"></el-col>
            <el-col :span="8"></el-col>
              <input type="file" ref="fileInput" @change="handleFileUpload">
              <el-button type="primary" @click="uploadFile" size="small">提交</el-button>
              <el-button type="primary" @click="orc" size="small">进行PDF版面分析</el-button>
              <el-button type="primary" @click="extractContent" size="small">进行信息抽取</el-button>
              <a v-if="zipfile" :href="zipfile"
                 style="margin-left: 5pt"
                 download>下载PDF分析后的zip文件</a>
          </el-row>
        </el-card>
        <el-card v-if="extractTriples">
          <el-row class="table" v-if="extractTriples">
          <el-table :data="extractTriples" v-if="showTriples">
            <el-table-column prop="subject" label="主体" width="180"></el-table-column>
            <el-table-column prop="predicate" label="关系类型" width="180"></el-table-column>
            <el-table-column prop="object" label="客体" width="180"></el-table-column>
          </el-table>
          </el-row>
        </el-card>
        <el-card class="card2">
          <el-row class="para-2">
            <el-col :span="8" :offset="6">
              <el-input class="inputText"
                        placeholder="请输入您的问题" v-model="question"></el-input>
            </el-col>
            <el-col :span="8">
              <el-button type="primary" @click="getAnswer" size="small">搜索</el-button>
            </el-col>
          </el-row>
            <el-row class="para-2">
              <el-col>
                <div class="outputText"
                          v-if="answer">
                  {{answer}}
                </div>
              </el-col>
            </el-row>
        </el-card>
      </el-main>
      <el-footer></el-footer>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'HelloWorld',
  data () {
    return {
      file: null,
      filename: null,
      question: "",
      zipfile: "",
      image: null,
      excelfile: null,
      extractTriples: null,
      showTriples: false,
      answer: ""
    }
  },
  methods: {
    handleFileUpload(event) {
      this.file = event.target.files[0]
      this.filename = this.file.name
    },
    uploadFile() {
      let that = this
      if (that.file === null || that.filename === null) {
        alert("请您先上传您的文件！")
        return
      }
      const formData = new FormData()
      formData.append('file', this.file)
      that.$http.request({
        url: that.$url + 'GetFile/',
        method: 'post',
        data: formData,
        params: {
          filename: that.filename
        }
      }).then(function (response) {
        console.log(response.data)
        alert("提交成功！")
      }).catch(function (error) {
        console.log(error)
      })
    },
    orc() {
      let that = this
      if (that.file === null || that.filename === null) {
        this.alert("请您先上传您的文件！")
        return
      }
      // 优先获得zipfile
      that.$http.request(
        {
          url: that.$url + 'ZipFile/',
          method: 'get',
          params: {
            filename: that.filename
          },
          responseType: 'blob'
        }
      ).then(function (response) {
        let blob = new Blob([response.data], {type: 'application/zip'})
        that.zipfile = URL.createObjectURL(blob)
        // console.log(response.data)
        console.log(that.zipfile)
        console.log(blob.size); // 输出 Blob 对象的大小
        console.log(blob.type); // 输出 Blob 对象的 MIME 类型
        console.log(blob.slice); // 输出 Blob 对象的切割方法
      }).catch(function (error) {
        // console.log(error)
      })
      //然后获得draw的图片
      // that.$http.request(
      //   {
      //     url: that.$url + 'DrawFile/',
      //     method: 'get',
      //     params: {
      //       filename: that.filename
      //     },
      //     responseType: 'arraybuffer'
      //   }
      // ).then(function (response) {
      //   let blob = new Blob([response.data], {type: 'image/jpeg'})
      //   that.image = URL.createObjectURL(blob)
      //   console.log(response.data)
      // }).catch(function (error) {
      //   console.log(error)
      // })
    },
    extractContent() {
      let that = this
      if (that.file === null || that.filename === null) {
        this.alert("请您先上传您的文件!")
        return
      }
      that.$http.request(
        {
          url: that.$url + 'ExtractFile/',
          method: 'get',
          params: {
            filename: that.filename
          }
        }
      ).then(function (response) {
        that.extractTriples = response.data
        that.showTriples = true
        console.log(response)
      }).catch(function (error) {
        console.log(error)
      })
    },
    getAnswer() {
      let that = this
      if (that.question === "") {
        that.alert("请输入问题！")
        return
      }
      that.$http.request({
        url: that.$url + 'QueryFile/',
        method: 'get',
        params: {
          question: that.question
        }
      }).then(function (response) {
        that.answer = response.data
        console.log(response)
      }).catch(function (error) {
        console.log(error)
      })
    }
  },
}
</script>
...

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
.table {
  padding-left: 15%;
}
.outputText {
  font-size: 15pt;
  font-family: 华文仿宋,serif;
  height: 25%;
  margin: 10pt 10pt 10pt 10pt;
  border-width: 4pt;
  box-shadow: gainsboro;
  border-style: dot-dot-dash;
  border-color: #a0cfff;
}
.el-card {
  margin-left: 15%;
  margin-right: 15%;
  margin-top: 1%;
}
.text {
    font-size: 14px;
  }

  .item {
    margin-bottom: 18px;
  }

  .clearfix:before,
  .clearfix:after {
    display: table;
    content: "";
  }
  .clearfix:after {
    clear: both
  }

  .box-card {
    width: 480px;
  }
</style>
