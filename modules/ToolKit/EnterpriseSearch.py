from langchain.tools import BaseTool

null = None

# 查询企业基本信息
class EnterpriseSearch(BaseTool):
    name = "企业基本信息查询"
    description = """用于查询企业基本信息。输出包含企业公司名称、注册资本、行业、法定代表人、统一社会信用代码等基本信息。"""

    def _run(self, query: str) -> str:
        # TODO : COT
        response = {
            "result":{
                "regCapital":"7426272.6645万人民币",
                "staffNumRange":"10000人以上",
                "bondNum":"601328",
                "industry":"货币金融服务",
                "bondName":"交通银行",
                "legalPersonName":"任德奇",
                "companyOrgType":"股份有限公司(上市、国有控股)",
                "orgNumber":"10000595-X",
                "email":"95559@bankcomm.com",
                "regInstitute":"上海市市场监督管理局",
                "businessScope":"吸收公众存款；发放短期、中期和长期贷款；办理国内外结算；办理票据承兑与贴现；发行金融债券；代理发行、代理兑付、承销政府债券；买卖政府债券、金融债券；从事同业拆借；买卖、代理买卖外汇；从事银行卡业务；提供信用证服务及担保；代理收付款项业务；提供保管箱服务；经各监督管理部门或者机构批准的其他业务（以许可批复文件为准）；经营结汇、售汇业务。【依法须经批准的项目，经相关部门批准后方可开展经营活动】",
                "taxNumber":"9131000010000595XD",
                "regLocation":"中国（上海）自由贸易试验区银城中路188号",
                "regCapitalCurrency":"人民币",
                "tags":"存续;A股 | 交通银行 601328 | 正常上市;港股 | 交通银行 HK.04605 | 正常上市;中概股 | 交通银行（ADR） BCMXY | 正常上市;项目品牌:交通银行;投资机构:交通银行;企业集团",
                "websiteList":"http://www.bankcomm.com/",
                "phoneNumber":"021-58781234",
                "district":"浦东新区",
                "bondType":"A股",
                "name":"交通银行股份有限公司",
                "percentileScore":9996,
                "industryAll":{
                    "categoryMiddle":"银行理财服务",
                    "categoryBig":"货币金融服务",
                    "category":"金融业",
                    "categorySmall":""
                },
            }
        }
        
        return response["result"]
    

if __name__ == "__main__":
    tool = EnterpriseSearch()
    print(tool._run(1))