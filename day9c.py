import gradio as gr
import pandas as pd

def 合并表格(文件1, 文件2):
    df1 = pd.read_excel(文件1.name)
    df2 = pd.read_excel(文件2.name)
    合并 = pd.concat([df1, df2], ignore_index=True)
    return 合并

demo = gr.Interface(
    fn=合并表格,
    inputs=[gr.File(label="第一个Excel"), gr.File(label="第二个Excel")],
    outputs=gr.Dataframe(label="合并结果"),
    title="Excel合并工具"
)

demo.launch()
