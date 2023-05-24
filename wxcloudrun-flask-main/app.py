from flask import Flask,request,jsonify
import numpy as np
from decimal import getcontext,Decimal
from fractions import Fraction
app = Flask(__name__)
getcontext().prec=2

# app.config['TEMPLATES_AUTO_RELOAD'] = True
def get_mo_no(fractions):
    fra_full=[]
    for i in fractions:
        fracline=[]
        for j in range(len(i)):
            if '/' in str(i[j]):
                frac_monu=str(i[j]).split('/')[0]
                frac_no=str(i[j]).split('/')[1]
            else:
                frac_monu=str(i[j])
                frac_no='1'
            fracline.append({'molecule':frac_monu,'denominator':frac_no})
        fra_full.append(fracline)
    return fra_full

@app.route('/',methods=['POST','GET'])
def parse_data():# put application's code here
    full_json=request.json
    print(full_json)
    np_p = numpy_process(full_json)
    np.set_printoptions( formatter={'all': lambda x: str(Fraction(x).limit_denominator())})
    result = np_p.src()
    print('已接收到发送来的数据')
    if full_json['process']!='finddet' and full_json['process']!='findrank':
        result=np.around(result, decimals=4)
        number_result=str(result.tolist())
        print(number_result)
        number_result=returnvaluetrans(number_result)
        print(number_result)

        fraction_result=result.tolist()
        fully_fra=get_mo_no(fraction_result)
        fully_result={'result':number_result,'fraction_result':fully_fra}
    elif full_json['process']=='finddet':
        print(result)
        result=np.around(result, decimals=4)
        fully_result={'result':str(Decimal(result)),'fraction_result':''}
    else:
        result=np.around(result, decimals=0)
        fully_result = {'result': str(result), 'fraction_result': ''}
    return jsonify(fully_result)

def returnvaluetrans(value):
    result=value.rstrip(']')
    result=result.lstrip('[')
    result=result.replace('], ','\n')
    result=result.replace(', ',' ')
    result=result.replace('[','')
    return result
class numpy_process():
    def __init__(self,full_data):
        self.full_data=full_data


    def txt2num(self,txt):
        matrix=[]
        txt_colunm=txt.split('\n')
        line=len(txt_colunm[0].split())
        for txt in txt_colunm:
            txt=list(map(eval,txt.split()))
            matrix.append(txt)
        return np.array(matrix).reshape(-1,line)

    def src(self):
        select=self.full_data['process']
        if select=='multiplymat':
            return self.multiplymat(self.full_data['matrix1']['txt'],self.full_data['matrix2']['txt'])
        if select=='matadd':
            return self.matadd(self.full_data['matrix1']['txt'],self.full_data['matrix2']['txt'],self.full_data['number1'],self.full_data['number2'])
        if select=='multiplynumber':
            return self.mutiplynumber(self.full_data['number'],self.full_data['matrix']['txt'])
        if select=='transmat':
            return self.transmat(self.full_data['matrix']['txt'])
        if select=='finddet':
            return self.finddet(self.full_data['matrix']['txt'])
        if select=='findinverse':
            return self.findinverse(self.full_data['matrix']['txt'])
        if select=='findaccompany':
            return self.findaccompany(self.full_data['matrix']['txt'])
        if select=='findrank':
            return self.findrank(self.full_data['matrix']['txt'])

    def multiplymat(self,mat1,mat2):
        matrix1=self.txt2num(mat1)
        matrix2=self.txt2num(mat2)
        return np.matmul(matrix1,matrix2)

    def matadd(self,mat1,mat2,num1,num2):
        matrix1 = self.txt2num(mat1)
        matrix2 = self.txt2num(mat2)
        return eval(num1)*matrix1+eval(num2)*matrix2

    def mutiplynumber(self,number,mat):
        matrix=self.txt2num(mat)
        return eval(number)*matrix

    def transmat(self,mat):
        matrix=self.txt2num(mat)
        return matrix.T

    def finddet(self,mat):
        matrix=self.txt2num(mat)
        result=np.linalg.det(matrix)
        return result

    def findinverse(self,mat):
        matrix=self.txt2num(mat)
        return np.linalg.inv(matrix)

    def findaccompany(self,mat):
        matrix=self.txt2num(mat)
        return np.linalg.inv(matrix)*np.linalg.det(matrix)

    def findrank(self,mat):
        matrix=self.txt2num(mat)
        return np.linalg.matrix_rank(matrix)


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=80)
