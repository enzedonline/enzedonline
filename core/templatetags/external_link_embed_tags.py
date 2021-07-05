import core.metadata 
# {
# url: https://www.abc.net.au/everyday/how-to-advance-your-career-when-you-work-for-yourself/100029812, 
# type: article, 
# title: Monica has a meeting with herself every Monday. Here's why - ABC Everyday, 
# description: When you work for yourself, you're responsible for everything to do with your job, including any plans for career progression., 
# image: https://live-production.wcms.abc-cdn.net.au/a54105739533622e77f3fce1d7cb7678?impolicy=wcms_crop_resize&cropH=1227&cropW=2182&xPos=184&yPos=314&width=862&height=485
# }

from django import template

register = template.Library()

@register.simple_tag()
def get_metadata(url):
    try:
        return core.metadata.get_metadata(url)
    except:
        return None
