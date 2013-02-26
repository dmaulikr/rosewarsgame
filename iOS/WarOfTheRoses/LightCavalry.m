//
//  LightCavalry.m
//  WarOfTheRoses
//
//  Created by Heine Skov Kristensen on 11/21/12.
//
//

#import "LightCavalry.h"

@implementation LightCavalry

-(id)init {
    self = [super init];
    
    if (self) {
        
        self.cardType = kCardTypeBasicUnit;
        self.unitType = kCavalry;
        self.unitName = kLightCavalry;
        
        self.attack = [[RangeAttribute alloc] initWithStartingRange:MakeAttributeRange(5, 6)];
        self.defence = [[RangeAttribute alloc] initWithStartingRange:MakeAttributeRange(1, 2)];
        self.range = 1;
        self.move = 4;
        self.moveActionCost = self.attackActionCost = 1;
        
        hasSpecialAbility = NO;
        
        self.attackSound = @"sword_sound.wav";

        self.frontImageSmall = @"lightcavalry_icon.png";
        self.frontImageLarge = [NSString stringWithFormat:@"lightcavalry_%d.png", self.cardColor];
        
        [self commonInit];
    }
    
    return self;
}

+ card {
    
    return [[LightCavalry alloc] init];
}

-(BOOL)specialAbilityTriggersVersus:(Card *)opponent {
    
    return NO;
}

- (void)addSpecialAbilityVersusOpponent:(Card *)opponent {
    
    
}

@end